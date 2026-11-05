from django.db import models
from django.utils import timezone


class Slider(models.Model):
    """
    کارگاه ۷: پیکربندی اسلایدر تصویر صفحه نخست
    """
    title = models.CharField(max_length=150, verbose_name="عنوان اسلاید")
    subtitle = models.CharField(max_length=250, blank=True, verbose_name="زیرعنوان / پیام ترغیب‌کننده")
    image = models.ImageField(upload_to='sliders/', null=True, blank=True, verbose_name="تصویر اسلاید")
    link = models.CharField(max_length=200, default='/shop/', verbose_name="نشانی پیوند (Link)")
    order = models.PositiveIntegerField(default=1, verbose_name="ترتیب نمایش اسلاید (کارگاه ۷)")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "اسلایدر تصویر"
        verbose_name_plural = "اسلایدرهای صفحه نخست (کارگاه ۷)"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.order}. {self.title}"


class Banner(models.Model):
    """
    کارگاه ۸: پیکربندی بنر صفحه اصلی
    """
    POSITION_CHOICES = [
        ('home_top', 'بالای صفحه اصلی'),
        ('home_middle', 'میانه صفحه اصلی (دوتایی)'),
        ('sidebar', 'ستون کناری (سایدبار)'),
    ]
    title = models.CharField(max_length=150, verbose_name="عنوان بنر")
    position = models.CharField(max_length=30, choices=POSITION_CHOICES, default='home_middle', verbose_name="موقعیت بنر")
    image = models.ImageField(upload_to='banners/', null=True, blank=True, verbose_name="تصویر بنر")
    link = models.CharField(max_length=200, default='/shop/', verbose_name="نشانی پیوند")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "بنر تبلیغاتی"
        verbose_name_plural = "بنرهای صفحه نخست (کارگاه ۸)"

    def __str__(self):
        return f"{self.get_position_display()} - {self.title}"


class Coupon(models.Model):
    """
    کارگاه ۲۳: ایجاد کد تخفیف برای مشتریان
    شامل تخفیف درصدی یا مبلغ ثابت، حداقل خرید، سقف و تاریخ اعتبار
    """
    TYPE_CHOICES = [
        ('percent', 'تخفیف درصدی (%)'),
        ('fixed', 'تخفیف مبلغ ثابت (تومان)'),
    ]
    code = models.CharField(max_length=50, unique=True, verbose_name="کد تخفیف (مثلاً NOBAHAR)")
    discount_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='percent', verbose_name="نوع تخفیف")
    value = models.PositiveIntegerField(verbose_name="مقدار تخفیف (درصد یا مبلغ به تومان)")
    min_order_amount = models.PositiveIntegerField(default=0, verbose_name="حداقل مبلغ خرید لازم (تومان)")
    max_discount_amount = models.PositiveIntegerField(null=True, blank=True, verbose_name="سقف تخفیف برای حالت درصدی (تومان)")
    
    valid_from = models.DateTimeField(default=timezone.now, verbose_name="تاریخ شروع اعتبار")
    valid_until = models.DateTimeField(verbose_name="تاریخ انقضا")
    
    usage_limit = models.PositiveIntegerField(default=100, verbose_name="حداکثر دفعات استفاده")
    used_count = models.PositiveIntegerField(default=0, verbose_name="تعداد دفعات استفاده‌شده")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "کد تخفیف"
        verbose_name_plural = "کدهای تخفیف (کارگاه ۲۳)"

    def __str__(self):
        return f"کد: {self.code} ({self.get_discount_type_display()}: {self.value})"

    def is_valid_for_amount(self, subtotal):
        now = timezone.now()
        if not self.is_active:
            return False, "این کد تخفیف غیرفعال است."
        if now < self.valid_from or now > self.valid_until:
            return False, "مهلت استفاده از این کد تخفیف به پایان رسیده است."
        if self.used_count >= self.usage_limit:
            return False, "ظرفیت استفاده از این کد تخفیف تکمیل شده است."
        if subtotal < self.min_order_amount:
            return False, f"حداقل مبلغ سفارش برای استفاده از این کد باید {self.min_order_amount:,} تومان باشد."
        return True, "کد تخفیف معتبر است."

    def calculate_discount(self, subtotal):
        if self.discount_type == 'percent':
            discount = (subtotal * self.value) // 100
            if self.max_discount_amount and discount > self.max_discount_amount:
                discount = self.max_discount_amount
            return discount
        else:
            return min(self.value, subtotal)
