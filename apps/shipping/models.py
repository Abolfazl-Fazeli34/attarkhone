from django.db import models


class Province(models.Model):
    """
    کارگاه ۱۰: پیکربندی مناطق، کشورها و استان‌ها
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="نام استان")
    is_active = models.BooleanField(default=True, verbose_name="فعال برای ارسال سفارش")

    class Meta:
        verbose_name = "استان و منطقه جغرافیایی"
        verbose_name_plural = "مناطق و استان‌ها (کارگاه ۱۰)"
        ordering = ['name']

    def __str__(self):
        return self.name


class Carrier(models.Model):
    """
    کارگاه ۱۰: تعریف حامل‌ها (شرکت‌های حمل و نقل پستی)
    """
    name = models.CharField(max_length=120, verbose_name="نام حامل (مثلاً پست پیشتاز، تیپاکس، پیک سلامت)")
    delivery_time = models.CharField(max_length=100, verbose_name="مدت زمان تقریبی تحویل (مثلاً ۲۴ الی ۴۸ ساعت)")
    cost = models.PositiveIntegerField(default=35000, verbose_name="هزینه ارسال پایه (تومان)")
    free_shipping_min_order = models.PositiveIntegerField(
        default=500000,
        verbose_name="حداقل سبد خرید برای ارسال رایگان (تومان)"
    )
    is_eco_friendly = models.BooleanField(
        default=True,
        verbose_name="دوستدار محیط زیست / بسته‌بندی سبز",
        help_text="توجهات زیست‌محیطی پودمان ۲: استفاده از وسایل نقلیه کم‌مصرف یا بسته‌بندی تجزیه‌پذیر"
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال در فروشگاه")

    class Meta:
        verbose_name = "حامل پستی"
        verbose_name_plural = "حامل‌ها و شیوه‌های ارسال (کارگاه ۱۰)"

    def __str__(self):
        return f"{self.name} - هزینه: {self.cost:,} تومان"
