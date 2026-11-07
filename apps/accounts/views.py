from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .models import User
from orders.models import Order, BankReceipt


class UserLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:home')
        form = AuthenticationForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        guest_session_key = request.session.session_key
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # انتقال و ادغام اقلام سبد خرید مهمان به حساب کاربری
            if guest_session_key:
                from orders.models import Cart
                guest_cart = Cart.objects.filter(session_key=guest_session_key).first()
                if guest_cart and guest_cart.items.exists():
                    user_cart, _ = Cart.objects.get_or_create(user=user)
                    for g_item in guest_cart.items.all():
                        existing = user_cart.items.filter(product=g_item.product, variant=g_item.variant).first()
                        if existing:
                            existing.quantity += g_item.quantity
                            existing.save()
                        else:
                            g_item.cart = user_cart
                            g_item.save()
                    guest_cart.delete()

            login(request, user)
            messages.success(request, f'خوش آمدید، {user.get_full_name() or user.username}!')
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            if user.is_store_staff:
                return redirect('accounts:staff_dashboard')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'نام کاربری یا گذرواژه نادرست است.')
            return render(request, 'accounts/login.html', {'form': form})


class UserRegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:home')
        return render(request, 'accounts/register.html')

    def post(self, request):
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if not username or not password or not phone:
            messages.error(request, 'تکمیل نام کاربری، شماره تماس و گذرواژه الزامی است.')
            return render(request, 'accounts/register.html')

        if password != password_confirm:
            messages.error(request, 'تکرار گذرواژه با گذرواژه همخوانی ندارد.')
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'این نام کاربری قبلاً ثبت شده است.')
            return render(request, 'accounts/register.html')

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            password=password,
            role='customer'
        )
        login(request, user)
        messages.success(request, 'حساب کاربری شما با موفقیت ایجاد شد.')
        return redirect('core:home')


class UserLogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, 'با موفقیت از حساب کاربری خارج شدید.')
        return redirect('core:home')


class UserProfileView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'accounts/profile.html', {'orders': orders})


class StaffDashboardView(View):
    """
    کارگاه ۱ و ۲: داشبورد اختصاصی کارمندان با تفکیک نقش‌ها
    (مدیر ارشد، حسابدار، انباردار/مسئول حمل، کارشناس پشتیبانی)
    """
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_store_staff:
            messages.warning(request, 'دسترسی به این بخش نیازمند نمایه کارمندی است.')
            return redirect('accounts:login')

        user = request.user
        role = user.role

        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending_payment').count()
        paid_orders = Order.objects.filter(status='paid').count()
        processing_orders = Order.objects.filter(status='processing').count()
        shipped_orders = Order.objects.filter(status='shipped').count()
        unverified_receipts = BankReceipt.objects.filter(is_verified=False).count()

        recent_orders = Order.objects.all().order_by('-created_at')[:10]
        recent_receipts = BankReceipt.objects.filter(is_verified=False).order_by('-created_at')[:10]

        context = {
            'user': user,
            'role': role,
            'role_display': user.role_display_fa,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'paid_orders': paid_orders,
            'processing_orders': processing_orders,
            'shipped_orders': shipped_orders,
            'unverified_receipts': unverified_receipts,
            'recent_orders': recent_orders,
            'recent_receipts': recent_receipts,
        }
        return render(request, 'accounts/staff_dashboard.html', context)

    def post(self, request):
        """تغییر سریع وضعیت سفارش توسط کارمند مجاز"""
        if not request.user.is_authenticated or not request.user.is_store_staff:
            return redirect('accounts:login')

        action = request.POST.get('action')
        order_id = request.POST.get('order_id')
        receipt_id = request.POST.get('receipt_id')

        if action == 'update_order_status' and order_id:
            order = Order.objects.get(id=order_id)
            new_status = request.POST.get('new_status')
            if new_status in dict(Order.STATUS_CHOICES):
                order.status = new_status
                order.save()
                messages.success(request, f'وضعیت سفارش {order.tracking_code} به «{order.get_status_display()}» تغییر یافت.')

        elif action == 'verify_receipt' and receipt_id:
            receipt = BankReceipt.objects.get(id=receipt_id)
            receipt.is_verified = True
            receipt.verified_by = request.user
            receipt.save()
            # وضعیت سفارش را به پرداخت شده تغییر می‌دهیم
            receipt.order.is_paid = True
            receipt.order.status = 'paid'
            receipt.order.save()
            messages.success(request, f'فیش بانکی سفارش {receipt.order.tracking_code} تایید شد و سفارش به حالت پرداخت شده تغییر یافت.')

        return redirect('accounts:staff_dashboard')
