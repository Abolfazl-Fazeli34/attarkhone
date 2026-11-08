from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils import timezone
from .models import User, EmailOTP
from orders.models import Order, BankReceipt
from core.emails import send_welcome_email, send_otp_verification_email


class UserLoginView(View):
    """
    ورود کاربر با نام کاربری یا نشانی ایمیل
    همراه با ادغام هوشمند سبد خرید مهمان به حساب کاربری
    """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:home')
        return render(request, 'accounts/login.html')

    def post(self, request):
        guest_session_key = request.session.session_key
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not identifier or not password:
            messages.error(request, 'لطفاً نام کاربری/ایمیل و گذرواژه را وارد کنید.')
            return render(request, 'accounts/login.html', {'identifier': identifier})

        user = authenticate(request, username=identifier, password=password)
        if user is not None:
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
            messages.error(request, 'نام کاربری/ایمیل یا گذرواژه وارد شده نادرست است.')
            return render(request, 'accounts/login.html', {'identifier': identifier})


class UserRegisterView(View):
    """
    ثبت‌نام کاربر جدید با اعتبارسنجی دو مرحله‌ای ایمیل (Email OTP)
    """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:home')
        return render(request, 'accounts/register.html')

    def post(self, request):
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if not username or not email or not password or not phone:
            messages.error(request, 'تکمیل نام کاربری، ایمیل، شماره تماس و گذرواژه الزامی است.')
            return render(request, 'accounts/register.html', {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
            })

        if '@' not in email or '.' not in email:
            messages.error(request, 'لطفاً یک نشانی ایمیل معتبر وارد فرمایید.')
            return render(request, 'accounts/register.html', {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
            })

        if password != password_confirm:
            messages.error(request, 'تکرار گذرواژه با گذرواژه اصلی همخوانی ندارد.')
            return render(request, 'accounts/register.html', {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
            })

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'این نام کاربری قبلاً در سامانه ثبت شده است.')
            return render(request, 'accounts/register.html', {
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
            })

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'این نشانی ایمیل قبلاً در سامانه ثبت گردیده است.')
            return render(request, 'accounts/register.html', {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
            })

        # ذخیره موقت اطلاعات در نشست و ارسال کد تایید ۵ رقمی به ایمیل
        request.session['pending_register'] = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'password': password
        }

        otp = EmailOTP.generate_code(email, purpose='register')
        send_otp_verification_email(email, otp.code, purpose='register', request=request)

        messages.info(request, f'کد تایید ۵ رقمی احراز هویت به نشانی {email} ارسال شد.')
        return redirect('accounts:verify_email')


class VerifyEmailOTPView(View):
    """
    تایید کد ۵ رقمی ارسال‌شده به ایمیل جهت نهایی‌سازی ثبت‌نام
    """
    def get(self, request):
        pending = request.session.get('pending_register')
        if not pending:
            messages.warning(request, 'لطفاً ابتدا فرم ثبت‌نام را تکمیل فرمایید.')
            return redirect('accounts:register')
        return render(request, 'accounts/verify_otp.html', {'email': pending.get('email')})

    def post(self, request):
        pending = request.session.get('pending_register')
        if not pending:
            messages.warning(request, 'نشست ثبت‌نام منقضی شده است. لطفاً مجدداً اقدام فرمایید.')
            return redirect('accounts:register')

        email = pending.get('email')
        code = request.POST.get('otp_code', '').strip()

        otp = EmailOTP.objects.filter(
            email__iexact=email,
            code=code,
            purpose='register',
            is_used=False,
            expires_at__gt=timezone.now()
        ).first()

        if not otp:
            messages.error(request, 'کد وارد شده نادرست است یا مهلت ۵ دقیقه‌ای آن به پایان رسیده است.')
            return render(request, 'accounts/verify_otp.html', {'email': email})

        # تایید موفقیت‌آمیز و ساخت قطعی کاربر
        user = User.objects.create_user(
            username=pending['username'],
            email=pending['email'],
            first_name=pending.get('first_name', ''),
            last_name=pending.get('last_name', ''),
            phone=pending.get('phone', ''),
            password=pending['password'],
            role='customer',
            email_verified=True
        )
        otp.is_used = True
        otp.save()

        request.session.pop('pending_register', None)
        send_welcome_email(user, request)
        login(request, user, backend='accounts.backends.EmailOrUsernameModelBackend')
        messages.success(request, 'نشانی رایانامه شما با موفقیت تایید شد و حساب کاربری ایجاد گردید!')
        return redirect('core:home')


class ResendOTPView(View):
    """
    ارسال مجدد کد تایید ایمیل
    """
    def post(self, request):
        pending = request.session.get('pending_register')
        if not pending:
            messages.warning(request, 'درخواستی برای ارسال مجدد یافت نشد.')
            return redirect('accounts:register')

        email = pending.get('email')
        otp = EmailOTP.generate_code(email, purpose='register')
        send_otp_verification_email(email, otp.code, purpose='register', request=request)
        messages.success(request, f'کد تایید ۵ رقمی جدید به نشانی {email} ارسال شد.')
        return redirect('accounts:verify_email')


class LoginWithOTPView(View):
    """
    ورود سریع بدون رمز عبور با کد یکبار مصرف ایمیل
    """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:home')
        return render(request, 'accounts/login_otp.html', {'step': 'enter_email'})

    def post(self, request):
        step = request.POST.get('step', 'send_otp')
        email = request.POST.get('email', '').strip().lower()

        if step == 'send_otp':
            if not email or '@' not in email:
                messages.error(request, 'لطفاً یک نشانی ایمیل معتبر وارد کنید.')
                return render(request, 'accounts/login_otp.html', {'step': 'enter_email'})

            user = User.objects.filter(email__iexact=email).first()
            if not user:
                messages.error(request, 'کاربری با این نشانی ایمیل یافت نشد. لطفاً ثبت‌نام نمایید.')
                return redirect('accounts:register')

            otp = EmailOTP.generate_code(email, purpose='login')
            send_otp_verification_email(email, otp.code, purpose='login', request=request)
            messages.info(request, f'کد ورود یکبار مصرف به {email} ارسال گردید.')
            return render(request, 'accounts/login_otp.html', {'step': 'enter_code', 'email': email})

        elif step == 'verify_otp':
            code = request.POST.get('otp_code', '').strip()
            otp = EmailOTP.objects.filter(
                email__iexact=email,
                code=code,
                purpose='login',
                is_used=False,
                expires_at__gt=timezone.now()
            ).first()

            if not otp:
                messages.error(request, 'کد وارد شده نامعتبر یا منقضی است.')
                return render(request, 'accounts/login_otp.html', {'step': 'enter_code', 'email': email})

            otp.is_used = True
            otp.save()

            user = User.objects.filter(email__iexact=email).first()
            if user:
                login(request, user, backend='accounts.backends.EmailOrUsernameModelBackend')
                messages.success(request, f'خوش آمدید، {user.get_full_name() or user.username}!')
                if user.is_seller:
                    return redirect('accounts:seller_dashboard')
                if user.is_store_staff:
                    return redirect('accounts:staff_dashboard')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'کاربر یافت نشد.')
                return redirect('accounts:login')


class PasswordResetRequestView(View):
    """
    درخواست بازیابی گذرواژه از طریق ارسال پیوند امن به ایمیل کاربر
    """
    def get(self, request):
        return render(request, 'accounts/password_reset.html')

    def post(self, request):
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'لطفاً نشانی ایمیل ثبت‌شده خود را وارد کنید.')
            return render(request, 'accounts/password_reset.html')

        user = User.objects.filter(email__iexact=email).first()
        if user:
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.http import urlsafe_base64_encode
            from django.utils.encoding import force_bytes
            from django.template.loader import render_to_string
            from django.core.mail import EmailMultiAlternatives
            from django.utils.html import strip_tags
            from django.conf import settings

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(f'/accounts/password-reset-confirm/{uid}/{token}/')

            context = {'user': user, 'reset_url': reset_url}
            html_body = render_to_string('emails/password_reset_email.html', context)
            text_body = strip_tags(html_body)

            try:
                msg = EmailMultiAlternatives(
                    subject='بازیابی گذرواژه حساب کاربری | عطارخونه',
                    body=text_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email]
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send(fail_silently=False)
            except Exception:
                pass

        messages.success(request, 'در صورتی که حسابی با این ایمیل وجود داشته باشد، پیوند بازیابی گذرواژه به صندوق ورودی شما ارسال گردید.')
        return redirect('accounts:login')


class PasswordResetConfirmView(View):
    """
    تایید پیوند بازیابی و تنظیم گذرواژه جدید
    """
    def get(self, request, uidb64, token):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_decode
        from django.utils.encoding import force_str

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            return render(request, 'accounts/password_reset_confirm.html', {'validlink': True, 'uidb64': uidb64, 'token': token})
        else:
            return render(request, 'accounts/password_reset_confirm.html', {'validlink': False})

    def post(self, request, uidb64, token):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_decode
        from django.utils.encoding import force_str

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')
            if not password or password != password_confirm:
                messages.error(request, 'گذرواژه‌ها یکسان نیستند یا فیلد خالی است.')
                return render(request, 'accounts/password_reset_confirm.html', {'validlink': True, 'uidb64': uidb64, 'token': token})

            user.set_password(password)
            user.save()
            messages.success(request, 'گذرواژه شما با موفقیت تغییر یافت. اکنون می‌توانید با گذرواژه جدید وارد شوید.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'پیوند بازیابی منقضی شده یا نامعتبر است.')
            return redirect('accounts:password_reset')


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
            from core.emails import send_order_confirmation_email
            send_order_confirmation_email(receipt.order, request)
            messages.success(request, f'فیش بانکی سفارش {receipt.order.tracking_code} تایید شد و سفارش به حالت پرداخت شده تغییر یافت.')

        return redirect('accounts:staff_dashboard')
