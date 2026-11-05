import uuid
from django.db import models
from django.conf import settings
from catalog.models import Product, ProductVariant
from shipping.models import Province, Carrier
from marketing.models import Coupon


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"

    def __str__(self):
        return f"سبد خرید {self.id} ({self.user or self.session_key})"

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="محصول")
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="مشخصه انتخابی")
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"

    @property
    def unit_price(self):
        if self.variant:
            return self.variant.price
        return self.product.final_price

    @property
    def total_price(self):
        return self.unit_price * self.quantity


class Order(models.Model):
    """
    کارگاه ۲۴: مدیریت سفارش‌ها و تغییر وضعیت‌ها
    شاخص ارزشیابی صفحه ۱۱۲ کتاب: تغییر وضعیت سفارشات، پیشنهاد کادوپیچی و تنظیمات سفارش
    """
    STATUS_CHOICES = [
        ('pending_payment', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده / ثبت اولیه'),
        ('processing', 'در حال آماده‌سازی و بسته‌بندی'),
        ('shipped', 'تحویل به حامل پستی / ارسال شده'),
        ('delivered', 'تحویل داده شده به مشتری'),
        ('cancelled', 'لغو شده'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('online', 'درگاه امن پرداخت آنلاین (شبیه‌ساز شاپرک)'),
        ('bank_receipt', 'پرداخت از طریق فیش بانکی و کارت‌به‌کارت (کارگاه ۱۷)'),
    ]

    tracking_code = models.CharField(max_length=32, unique=True, verbose_name="کد رهگیری سفارش")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name="مشتری"
    )
    
    # اطلاعات تحویل گیرنده
    full_name = models.CharField(max_length=150, verbose_name="نام و نام خانوادگی تحویل‌گیرنده")
    phone = models.CharField(max_length=20, verbose_name="تلفن همراه")
    email = models.EmailField(blank=True, verbose_name="ایمیل")
    province = models.ForeignKey(Province, on_delete=models.PROTECT, verbose_name="استان (کارگاه ۱۰)")
    city = models.CharField(max_length=100, verbose_name="شهر")
    address = models.TextField(verbose_name="نشانی دقیق پستی")
    postal_code = models.CharField(max_length=20, verbose_name="کد پستی ۱۰ رقمی")
    order_notes = models.TextField(blank=True, verbose_name="یادداشت و توضیحات خریدار")

    # حامل و ارسال (کارگاه ۱۰)
    carrier = models.ForeignKey(Carrier, on_delete=models.PROTECT, verbose_name="حامل انتخابی (کارگاه ۱۰)")
    shipping_cost = models.PositiveIntegerField(default=0, verbose_name="هزینه ارسال (تومان)")

    # کادوپیچی ویژه (کارگاه ۲۴ و شاخص ارزشیابی ص ۱۱۲)
    is_gift_wrapped = models.BooleanField(
        default=False,
        verbose_name="پیشنهاد کادوپیچی ویژه هدیه (ارزشیابی پودمان ۲)",
        help_text="بسته‌بندی تزئینی شکیل با روبان و کاغذ کرافت گیاهی دوستدار محیط زیست"
    )
    gift_message = models.TextField(
        blank=True,
        verbose_name="متن کارت تبریک / یادداشت هدیه"
    )
    gift_cost = models.PositiveIntegerField(default=0, verbose_name="هزینه کادوپیچی (تومان)")

    # کد تخفیف (کارگاه ۲۳)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="کد تخفیف استفاده‌شده")
    discount_amount = models.PositiveIntegerField(default=0, verbose_name="مبلغ تخفیف (تومان)")

    # مبالغ
    subtotal = models.PositiveIntegerField(verbose_name="جمع اقلام (تومان)")
    total_amount = models.PositiveIntegerField(verbose_name="مبلغ نهایی قابل پرداخت (تومان)")

    # شیوه پرداخت و وضعیت
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='online', verbose_name="روش پرداخت")
    is_paid = models.BooleanField(default=False, verbose_name="وضعیت تسویه مالی")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_payment', verbose_name="وضعیت سفارش (کارگاه ۲۴)")
    
    admin_notes = models.TextField(blank=True, verbose_name="یادداشت مدیریتی / کد رهگیری پستی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین به‌روزرسانی")

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها و صورت‌حساب‌ها (کارگاه ۲۴)"
        ordering = ['-created_at']

    def __str__(self):
        return f"سفارش {self.tracking_code} - {self.full_name} ({self.get_status_display()})"

    @classmethod
    def generate_tracking_code(cls):
        import random
        return f"ATK-{random.randint(100000, 999999)}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="سفارش")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="محصول")
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="مشخصه")
    product_name = models.CharField(max_length=200, verbose_name="نام محصول در زمان خرید")
    variant_label = models.CharField(max_length=100, blank=True, verbose_name="مشخصه در زمان خرید")
    price = models.PositiveIntegerField(verbose_name="قیمت واحد (تومان)")
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")

    class Meta:
        verbose_name = "قلم سفارش"
        verbose_name_plural = "اقلام سفارش"

    @property
    def total_price(self):
        return self.price * self.quantity


class BankReceipt(models.Model):
    """
    کارگاه ۱۷: پیکربندی پرداخت از طریق فیش بانکی (کارت‌به‌کارت و واریز بانکی)
    """
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='receipt', verbose_name="سفارش مربوطه")
    bank_name = models.CharField(max_length=100, verbose_name="نام بانک مبدا یا مقصد (مثلاً بانک ملی یا صادرات)")
    tracking_number = models.CharField(max_length=100, verbose_name="شماره پیگیری / ارجاع فیش")
    card_last_digits = models.CharField(max_length=4, blank=True, verbose_name="۴ رقم آخر کارت واریزکننده")
    deposited_amount = models.PositiveIntegerField(verbose_name="مبلغ واریز شده (تومان)")
    receipt_image = models.ImageField(upload_to='receipts/', blank=True, null=True, verbose_name="تصویر رسید فیش واریزی")
    
    is_verified = models.BooleanField(default=False, verbose_name="تایید واریز توسط حسابداری (کارگاه ۱ و ۱۷)")
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="کارمند تاییدکننده (نقش حسابدار)"
    )
    admin_comment = models.CharField(max_length=255, blank=True, verbose_name="توضیح کارشناس حسابداری")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت فیش")

    class Meta:
        verbose_name = "فیش بانکی واریزی"
        verbose_name_plural = "فیش‌های بانکی واریزی (کارگاه ۱۷)"

    def __str__(self):
        return f"فیش سفارش {self.order.tracking_code} - رهگیری: {self.tracking_number}"
