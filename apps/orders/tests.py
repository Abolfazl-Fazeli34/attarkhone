from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta

from marketing.models import Coupon
from orders.models import Order, OrderItem
from shipping.models import Province, Carrier
from catalog.models import Product, Category
from core.models import StoreSetting


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

    def test_coupon_calculation(self):
        # تست اعتبار کوپن برای مبلغ کمتر از حداقل
        valid, msg = self.coupon_percent.is_valid_for_amount(30000)
        self.assertFalse(valid)

        # تست اعتبار کوپن برای مبلغ مجاز
        valid, msg = self.coupon_percent.is_valid_for_amount(100000)
        self.assertTrue(valid)

        # محاسبه ۲۰ درصد از ۱۰۰۰۰۰ = ۲۰۰۰۰
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
