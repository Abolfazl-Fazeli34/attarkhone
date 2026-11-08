from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
import random

from .models import Cart, CartItem, Order, OrderItem, BankReceipt
from .zarinpal import request_zarinpal_payment, verify_zarinpal_payment
from catalog.models import Product, ProductVariant
from shipping.models import Province, Carrier
from marketing.models import Coupon
from core.models import StoreSetting
from core.emails import send_order_confirmation_email


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.save()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


class CartView(View):
    """
    سبد خرید فروشگاه
    پوشش کارگاه ۲۳ (اعمال کوپن تخفیف)
    پوشش کارگاه ۲۴ (پیشنهاد کادوپیچی ویژه و درج پیام هدیه)
    """
    def get(self, request):
        cart = get_or_create_cart(request)
        setting = StoreSetting.get_settings()
        
        # اطلاعات کادوپیچی و کوپن از نشست
        is_gift_wrapped = request.session.get('cart_is_gift_wrapped', False)
        gift_message = request.session.get('cart_gift_message', '')
        gift_cost = setting.gift_wrap_cost if is_gift_wrapped else 0

        # محاسبه کوپن
        coupon_code = request.session.get('cart_coupon_code')
        coupon = None
        discount_amount = 0
        coupon_error = None

        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                is_valid, msg = coupon.is_valid_for_amount(cart.subtotal)
                if is_valid:
                    discount_amount = coupon.calculate_discount(cart.subtotal)
                else:
                    coupon_error = msg
                    del request.session['cart_coupon_code']
            except Coupon.DoesNotExist:
                del request.session['cart_coupon_code']

        subtotal = cart.subtotal
        total_payable = max(0, subtotal - discount_amount + gift_cost)

        context = {
            'cart': cart,
            'subtotal': subtotal,
            'is_gift_wrapped': is_gift_wrapped,
            'gift_message': gift_message,
            'gift_cost': gift_cost,
            'setting_gift_cost': setting.gift_wrap_cost,
            'coupon': coupon,
            'discount_amount': discount_amount,
            'coupon_error': coupon_error,
            'total_payable': total_payable,
        }
        return render(request, 'orders/cart.html', context)

    def post(self, request):
        """به‌روزرسانی تنظیمات کادوپیچی و یادداشت هدیه در سبد خرید"""
        action = request.POST.get('action')
        if action == 'update_gift':
            is_gift = request.POST.get('is_gift_wrapped') == 'on'
            msg = request.POST.get('gift_message', '').strip()
            request.session['cart_is_gift_wrapped'] = is_gift
            request.session['cart_gift_message'] = msg
            messages.success(request, 'تنظیمات کادوپیچی هدیه با موفقیت به‌روزرسانی شد.')
        return redirect('orders:cart')


class AddToCartView(View):
    def post(self, request, product_id):
        cart = get_or_create_cart(request)
        product = get_object_or_404(Product, id=product_id)
        
        variant_id = request.POST.get('variant_id')
        variant = None
        if variant_id and variant_id.isdigit():
            variant = get_object_or_404(ProductVariant, id=int(variant_id), product=product)

        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        messages.success(request, f'«{product.name}» به سبد خرید افزوده شد.')
        return redirect('orders:cart')


class AddToCartAjaxView(View):
    """
    افزودن بلادرنگ کالا به سبد خرید با ایجکس (بدون بارگذاری مجدد صفحه)
    """
    def post(self, request, product_id):
        cart = get_or_create_cart(request)
        product = get_object_or_404(Product, id=product_id)
        
        variant_id = request.POST.get('variant_id')
        variant = None
        if variant_id and str(variant_id).isdigit():
            variant = ProductVariant.objects.filter(id=int(variant_id), product=product).first()

        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        total_items = sum(item.quantity for item in cart.items.all())
        return JsonResponse({
            'success': True,
            'message': f'«{product.name}» با موفقیت به سبد خرید افزوده شد.',
            'cart_count': total_items,
            'cart_subtotal': f"{cart.subtotal:,}",
            'item_quantity': cart_item.quantity,
        })


class UpdateQuantityAjaxView(View):
    """
    افزایش یا کاهش استپر تعداد در سبد خرید به صورت ایجکس
    """
    def post(self, request, item_id):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        action = request.POST.get('action')

        if action == 'increase':
            item.quantity += 1
            item.save()
        elif action == 'decrease':
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()
                total_items = sum(i.quantity for i in cart.items.all())
                return JsonResponse({
                    'success': True,
                    'is_deleted': True,
                    'item_id': item_id,
                    'cart_count': total_items,
                    'cart_subtotal': f"{cart.subtotal:,}",
                    'message': 'کالا از سبد خرید حذف شد.'
                })

        total_items = sum(i.quantity for i in cart.items.all())
        return JsonResponse({
            'success': True,
            'is_deleted': False,
            'item_id': item_id,
            'quantity': item.quantity,
            'item_total': f"{item.total_price:,}",
            'cart_count': total_items,
            'cart_subtotal': f"{cart.subtotal:,}",
        })


class RemoveItemAjaxView(View):
    """
    حذف بلادرنگ کالا از سبد خرید با ایجکس
    """
    def post(self, request, item_id):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        name = item.product.name
        item.delete()
        total_items = sum(i.quantity for i in cart.items.all())
        return JsonResponse({
            'success': True,
            'item_id': item_id,
            'message': f'«{name}» از سبد خرید حذف شد.',
            'cart_count': total_items,
            'cart_subtotal': f"{cart.subtotal:,}",
        })


class RemoveFromCartView(View):
    def post(self, request, item_id):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        name = item.product.name
        item.delete()
        messages.info(request, f'«{name}» از سبد خرید حذف شد.')
        return redirect('orders:cart')


class ApplyCouponView(View):
    """
    کارگاه ۲۳: بررسی و اعمال کد تخفیف در سبد خرید
    """
    def post(self, request):
        code = request.POST.get('code', '').strip()
        cart = get_or_create_cart(request)

        if not code:
            messages.warning(request, 'لطفاً کد تخفیف را وارد کنید.')
            return redirect('orders:cart')

        try:
            coupon = Coupon.objects.get(code__iexact=code)
            is_valid, msg = coupon.is_valid_for_amount(cart.subtotal)
            if is_valid:
                request.session['cart_coupon_code'] = coupon.code
                discount = coupon.calculate_discount(cart.subtotal)
                messages.success(request, f'کد تخفیف «{coupon.code}» اعمال شد ({discount:,} تومان کسر گردید).')
            else:
                messages.error(request, msg)
        except Coupon.DoesNotExist:
            messages.error(request, 'کد تخفیف وارد شده معتبر نمی‌باشد.')

        return redirect('orders:cart')


class RemoveCouponView(View):
    def post(self, request):
        if 'cart_coupon_code' in request.session:
            del request.session['cart_coupon_code']
            messages.info(request, 'کد تخفیف از سبد خرید حذف گردید.')
        return redirect('orders:cart')


class CheckoutView(View):
    """
    مرحله نهایی ثبت سفارش
    کارگاه ۱۰ (انتخاب حامل و استان)
    کارگاه ۱۷ (روش پرداخت فیش بانکی یا درگاه آنلاین)
    کارگاه ۲۴ (ذخیره اطلاعات کادوپیچی و صدور فاکتور)
    """
    def get(self, request):
        if not request.user.is_authenticated:
            messages.info(request, 'برای تکمیل سفارش و پرداخت، لطفاً ابتدا وارد حساب کاربری خود شوید.')
            return redirect(f'/accounts/login/?next={request.path}')

        cart = get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, 'سبد خرید شما خالی است.')
            return redirect('catalog:product_list')

        provinces = Province.objects.filter(is_active=True)
        carriers = Carrier.objects.filter(is_active=True)
        setting = StoreSetting.get_settings()

        is_gift_wrapped = request.session.get('cart_is_gift_wrapped', False)
        gift_message = request.session.get('cart_gift_message', '')
        gift_cost = setting.gift_wrap_cost if is_gift_wrapped else 0

        # محاسبه تخفیف کوپن
        coupon_code = request.session.get('cart_coupon_code')
        coupon = None
        discount_amount = 0
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                is_valid, _ = coupon.is_valid_for_amount(cart.subtotal)
                if is_valid:
                    discount_amount = coupon.calculate_discount(cart.subtotal)
            except Coupon.DoesNotExist:
                pass

        subtotal = cart.subtotal
        context = {
            'cart': cart,
            'provinces': provinces,
            'carriers': carriers,
            'subtotal': subtotal,
            'is_gift_wrapped': is_gift_wrapped,
            'gift_message': gift_message,
            'gift_cost': gift_cost,
            'coupon': coupon,
            'discount_amount': discount_amount,
        }
        return render(request, 'orders/checkout.html', context)

    def post(self, request):
        if not request.user.is_authenticated:
            messages.info(request, 'برای تکمیل سفارش و پرداخت، لطفاً ابتدا وارد حساب کاربری خود شوید.')
            return redirect(f'/accounts/login/?next={request.path}')

        cart = get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, 'سبد خرید شما خالی است.')
            return redirect('catalog:product_list')

        # دریافت ورودی‌های فرم
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        province_id = request.POST.get('province')
        city = request.POST.get('city', '').strip()
        address = request.POST.get('address', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        order_notes = request.POST.get('order_notes', '').strip()
        carrier_id = request.POST.get('carrier')
        payment_method = request.POST.get('payment_method', 'online')

        if not all([full_name, phone, province_id, city, address, postal_code, carrier_id]):
            messages.error(request, 'لطفاً تمامی فیلدهای الزامی فرم تحویل را تکمیل نمایید.')
            return redirect('orders:checkout')

        province = get_object_or_404(Province, id=province_id)
        carrier = get_object_or_404(Carrier, id=carrier_id)
        setting = StoreSetting.get_settings()

        # محاسبه هزینه ارسال
        subtotal = cart.subtotal
        if subtotal >= carrier.free_shipping_min_order:
            shipping_cost = 0
        else:
            shipping_cost = carrier.cost

        # کادوپیچی
        is_gift_wrapped = request.session.get('cart_is_gift_wrapped', False)
        gift_message = request.session.get('cart_gift_message', '')
        gift_cost = setting.gift_wrap_cost if is_gift_wrapped else 0

        # کوپن تخفیف
        coupon_code = request.session.get('cart_coupon_code')
        coupon = None
        discount_amount = 0
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                is_valid, _ = coupon.is_valid_for_amount(subtotal)
                if is_valid:
                    discount_amount = coupon.calculate_discount(subtotal)
                    coupon.used_count += 1
                    coupon.save()
            except Coupon.DoesNotExist:
                pass

        total_amount = max(0, subtotal - discount_amount + shipping_cost + gift_cost)

        # ساخت رکورد سفارش
        order = Order.objects.create(
            tracking_code=Order.generate_tracking_code(),
            user=request.user if request.user.is_authenticated else None,
            full_name=full_name,
            phone=phone,
            email=email,
            province=province,
            city=city,
            address=address,
            postal_code=postal_code,
            order_notes=order_notes,
            carrier=carrier,
            shipping_cost=shipping_cost,
            is_gift_wrapped=is_gift_wrapped,
            gift_message=gift_message,
            gift_cost=gift_cost,
            coupon=coupon,
            discount_amount=discount_amount,
            subtotal=subtotal,
            total_amount=total_amount,
            payment_method=payment_method,
            status='pending_payment',
        )

        # انتقال اقلام سبد خرید به OrderItem
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                variant=item.variant,
                product_name=item.product.name,
                variant_label=item.variant.weight_label if item.variant else '',
                price=item.unit_price,
                quantity=item.quantity,
            )

        # خالی کردن سبد خرید و نشست
        cart.items.all().delete()
        request.session.pop('cart_is_gift_wrapped', None)
        request.session.pop('cart_gift_message', None)
        request.session.pop('cart_coupon_code', None)

        if payment_method == 'bank_receipt':
            messages.info(request, f'سفارش شما با شماره رهگیری {order.tracking_code} ثبت گردید. لطفاً اطلاعات فیش واریزی را تکمیل کنید.')
            return redirect('orders:bank_receipt', tracking_code=order.tracking_code)
        else:
            # ارسال به درگاه رسمی اینترنتی زرین‌پال شاپرک
            callback_url = request.build_absolute_uri(
                reverse('orders:zarinpal_callback', kwargs={'tracking_code': order.tracking_code})
            )
            zp_res = request_zarinpal_payment(order, callback_url, request=request)
            return redirect(zp_res['redirect_url'])


class ZarinpalGatewayView(View):
    """
    درگاه پرداخت اینترنتی زرین‌پال (شاپرک / سندباکس رسمی)
    """
    def get(self, request, tracking_code):
        order = get_object_or_404(Order, tracking_code=tracking_code)
        if order.is_paid:
            return redirect('orders:invoice', tracking_code=order.tracking_code)
        return render(request, 'orders/zarinpal_gateway.html', {'order': order})


class ZarinpalCallbackView(View):
    """
    دریافت بازگشت تراکنش از درگاه زرین‌پال و تایید نهایی پرداخت
    """
    def get(self, request, tracking_code):
        order = get_object_or_404(Order, tracking_code=tracking_code)
        authority = request.GET.get('Authority', order.zarinpal_authority)
        status = request.GET.get('Status', 'NOK')

        is_verified, msg, ref_id = verify_zarinpal_payment(order, authority, status)
        if is_verified:
            order.is_paid = True
            order.status = 'paid'
            order.admin_notes = f"پرداخت آنلاین موفق از طریق درگاه زرین‌پال شاپرک - شناسه مرجع بانکی: {ref_id}"
            order.save()

            # کسر موجودی انبار و ثبت آمار فروش (کارگاه ۲۴)
            for oi in order.items.all():
                p = oi.product
                p.stock = max(0, p.stock - oi.quantity)
                p.sales_count += oi.quantity
                p.save()

            # ارسال خودکار رایانامه فاکتور و رسید سفارش به خریدار
            send_order_confirmation_email(order, request)

            messages.success(request, f'پرداخت با موفقیت در درگاه زرین‌پال تایید شد! شناسه پیگیری بانکی: {ref_id}')
            return redirect('orders:invoice', tracking_code=order.tracking_code)
        else:
            messages.error(request, f'تراکنش پرداخت زرین‌پال لغو یا ناموفق بود: {msg}')
            return redirect('orders:invoice', tracking_code=order.tracking_code)


class MockPaymentGatewayView(View):
    """
    جهت سازگاری با درخواست‌های قبلی و تست‌های شبیه‌ساز پرداخت شاپرک
    """
    def get(self, request, tracking_code):
        return redirect('orders:zarinpal_gateway_view', tracking_code=tracking_code)

    def post(self, request, tracking_code):
        order = get_object_or_404(Order, tracking_code=tracking_code)
        action = request.POST.get('action')
        if action == 'pay_success':
            order.is_paid = True
            order.status = 'paid'
            order.admin_notes = "پرداخت موفق از طریق شبیه‌ساز بانکی شاپرک / زرین‌پال"
            order.save()
            for oi in order.items.all():
                p = oi.product
                p.stock = max(0, p.stock - oi.quantity)
                p.sales_count += oi.quantity
                p.save()
            send_order_confirmation_email(order, request)
            messages.success(request, 'پرداخت موفق ثبت گردید.')
            return redirect('orders:invoice', tracking_code=order.tracking_code)
        elif action == 'pay_fail':
            messages.error(request, 'پرداخت لغو شد.')
            return redirect('orders:invoice', tracking_code=order.tracking_code)
        return redirect('orders:zarinpal_gateway_view', tracking_code=tracking_code)


class BankReceiptView(View):
    """
    کارگاه ۱۷: ثبت اطلاعات فیش بانکی و کارت‌به‌کارت
    """
    def get(self, request, tracking_code):
        order = get_object_or_404(Order, tracking_code=tracking_code)
        setting = StoreSetting.get_settings()
        context = {
            'order': order,
            'setting': setting,
        }
        return render(request, 'orders/bank_receipt.html', context)

    def post(self, request, tracking_code):
        order = get_object_or_404(Order, tracking_code=tracking_code)
        bank_name = request.POST.get('bank_name', '').strip()
        tracking_number = request.POST.get('tracking_number', '').strip()
        card_last_digits = request.POST.get('card_last_digits', '').strip()
        receipt_image = request.FILES.get('receipt_image')

        if not bank_name or not tracking_number:
            messages.error(request, 'نام بانک و شماره پیگیری فیش الزامی است.')
            return redirect('orders:bank_receipt', tracking_code=order.tracking_code)

        BankReceipt.objects.update_or_create(
            order=order,
            defaults={
                'bank_name': bank_name,
                'tracking_number': tracking_number,
                'card_last_digits': card_last_digits,
                'deposited_amount': order.total_amount,
                'receipt_image': receipt_image,
            }
        )

        send_order_confirmation_email(order, request)

        messages.success(request, 'فیش بانکی با موفقیت ثبت شد و پس از بررسی حسابداری، وضعیت سفارش به‌روزرسانی خواهد شد.')
        return redirect('orders:invoice', tracking_code=order.tracking_code)


class OrderInvoiceView(View):
    """
    کارگاه ۲۴: چاپ و مشاهده پیش‌فاکتور و فاکتور نهایی فروش
    همراه با مهر، بارکد، جدول اقلام، هزینه کادوپیچی و اطلاعات حامل
    """
    def get(self, request, tracking_code):
        order = get_object_or_404(Order.objects.select_related('carrier', 'province', 'coupon').prefetch_related('items'), tracking_code=tracking_code)
        setting = StoreSetting.get_settings()
        context = {
            'order': order,
            'setting': setting,
        }
        return render(request, 'orders/invoice.html', context)


class OrderTrackingView(View):
    """
    پیگیری آنلاین وضعیت سفارش با کد رهگیری
    """
    def get(self, request):
        code = request.GET.get('code', '').strip()
        order = None
        if code:
            order = Order.objects.filter(tracking_code__iexact=code).first()
            if not order:
                messages.warning(request, 'سفارشی با این شماره رهگیری یافت نشد.')

        return render(request, 'orders/tracking.html', {'order': order, 'search_code': code})
