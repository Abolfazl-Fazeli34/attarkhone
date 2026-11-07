from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from marketing.models import Coupon
from orders.models import Order, OrderItem, Cart, CartItem
from shipping.models import Province, Carrier
from catalog.models import Product, Category
from core.models import StoreSetting

User = get_user_model()


class CouponAndOrderTestCase(TestCase):
    def setUp(self):
        self.province = Province.objects.create(name="تهران")
        self.carrier = Carrier.objects.create(
            name="پست پیشتاز",
            cost=30000,
            free_shipping_min_order=200000
        )
        self.category = Category.objects.create(name="گیاهان دارویی", slug="herbs")
        self.product = Product.objects.create(
            name="گل گاوزبان",
            slug="gol-gavzaban",
            category=self.category,
            base_price=50000,
            stock=10,
        )

        now = timezone.now()
        self.coupon_percent = Coupon.objects.create(
            code="OFF20",
            discount_type="percent",
            value=20,
            min_order_amount=50000,
            max_discount_amount=40000,
            valid_from=now - timedelta(days=1),
            valid_until=now + timedelta(days=10),
            usage_limit=10,
        )

        self.user = User.objects.create_user(
            username="test_customer",
            password="Password123!",
            first_name="علی",
            last_name="محمدی",
            phone="09121112233"
        )

    def test_coupon_calculation(self):
        valid, msg = self.coupon_percent.is_valid_for_amount(30000)
        self.assertFalse(valid)

        valid, msg = self.coupon_percent.is_valid_for_amount(100000)
        self.assertTrue(valid)

        discount = self.coupon_percent.calculate_discount(100000)
        self.assertEqual(discount, 20000)

    def test_order_creation_with_gift_wrapping(self):
        """تست کارگاه ۲۴ و شاخص ارزشیابی ص ۱۱۲: پیشنهاد کادوپیچی و ثبت متن هدیه"""
        order = Order.objects.create(
            tracking_code=Order.generate_tracking_code(),
            full_name="مریم احمدی",
            phone="09123456789",
            province=self.province,
            city="تهران",
            address="خیابان آزادی",
            postal_code="1234567890",
            carrier=self.carrier,
            shipping_cost=self.carrier.cost,
            is_gift_wrapped=True,
            gift_message="تولدتان مبارک با آرزوی تندرستی و نشاط",
            gift_cost=25000,
            subtotal=100000,
            total_amount=155000,
            payment_method="online",
            status="pending_payment"
        )

        self.assertTrue(order.is_gift_wrapped)
        self.assertEqual(order.gift_cost, 25000)
        self.assertIn("تولدتان مبارک", order.gift_message)
        self.assertEqual(order.status, "pending_payment")

    def test_ajax_cart_operations(self):
        """تست افزودن و تغییر تعداد کالا در سبد خرید با ایجکس"""
        client = Client()
        # افزودن به سبد
        response = client.post(reverse('orders:add_to_cart_ajax', kwargs={'product_id': self.product.id}), {
            'quantity': 2
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['cart_count'], 2)

        # استخراج آیتم سبد خرید
        cart_item = CartItem.objects.first()
        self.assertIsNotNone(cart_item)
        self.assertEqual(cart_item.quantity, 2)

        # افزایش استپر
        res_step = client.post(reverse('orders:update_quantity_ajax', kwargs={'item_id': cart_item.id}), {
            'action': 'increase'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res_step.status_code, 200)
        data_step = res_step.json()
        self.assertEqual(data_step['quantity'], 3)
        self.assertEqual(data_step['cart_count'], 3)

        # کاهش استپر تا حذف
        client.post(reverse('orders:update_quantity_ajax', kwargs={'item_id': cart_item.id}), {
            'action': 'decrease'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        client.post(reverse('orders:update_quantity_ajax', kwargs={'item_id': cart_item.id}), {
            'action': 'decrease'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        res_del = client.post(reverse('orders:update_quantity_ajax', kwargs={'item_id': cart_item.id}), {
            'action': 'decrease'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTrue(res_del.json()['is_deleted'])
        self.assertEqual(CartItem.objects.count(), 0)

    def test_checkout_requires_authentication(self):
        """بررسی هدایت کاربر مهمان به صفحه ورود هنگام مراجعه به تسویه حساب"""
        client = Client()
        # افزودن کالا تا سبد خالی نباشد
        client.post(reverse('orders:add_to_cart_ajax', kwargs={'product_id': self.product.id}), {'quantity': 1})
        
        response = client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_cart_merge_on_login(self):
        """ادغام سبد خرید مهمان با سبد خرید کاربر پس از ورود به سیستم"""
        client = Client()
        # ۱. مهمان کالا اضافه می‌کند
        client.post(reverse('orders:add_to_cart_ajax', kwargs={'product_id': self.product.id}), {'quantity': 2})
        guest_cart = Cart.objects.filter(session_key=client.session.session_key).first()
        self.assertIsNotNone(guest_cart)
        self.assertEqual(guest_cart.items.count(), 1)

        # ۲. ورود کاربر به سیستم
        login_res = client.post(reverse('accounts:login'), {
            'username': 'test_customer',
            'password': 'Password123!'
        })
        self.assertEqual(login_res.status_code, 302)

        # ۳. بررسی انتقال آیتم به سبد کاربر
        user_cart = Cart.objects.filter(user=self.user).first()
        self.assertIsNotNone(user_cart)
        self.assertEqual(user_cart.items.count(), 1)
        self.assertEqual(user_cart.items.first().quantity, 2)

    def test_payment_success_deducts_inventory(self):
        """تست کسر موجودی انبار و افزایش فروش پس از پرداخت موفق در شبیه‌ساز شاپرک"""
        client = Client()
        initial_stock = self.product.stock
        initial_sales = self.product.sales_count

        order = Order.objects.create(
            tracking_code=Order.generate_tracking_code(),
            user=self.user,
            full_name="علی محمدی",
            phone="09121112233",
            province=self.province,
            city="تهران",
            address="خیابان آزادی",
            postal_code="1234567890",
            carrier=self.carrier,
            shipping_cost=self.carrier.cost,
            subtotal=self.product.base_price * 2,
            total_amount=self.product.base_price * 2 + self.carrier.cost,
            payment_method="online",
            status="pending_payment"
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name=self.product.name,
            price=self.product.base_price,
            quantity=2
        )

        # شبیه‌سازی پرداخت موفق در شاپرک
        pay_res = client.post(reverse('orders:mock_gateway', kwargs={'tracking_code': order.tracking_code}), {
            'action': 'pay_success'
        })
        self.assertEqual(pay_res.status_code, 302)

        order.refresh_from_db()
        self.assertTrue(order.is_paid)
        self.assertEqual(order.status, 'paid')

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock - 2)
        self.assertEqual(self.product.sales_count, initial_sales + 2)
