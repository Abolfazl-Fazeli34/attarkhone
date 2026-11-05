from django.db import models


class StoreSetting(models.Model):
    """
    تنظیمات سراسری فروشگاه
    پوشش کارگاه ۳ (حالت تعمیرات و IP مجاز)
    پوشش کارگاه ۴ (تنظیم نام و اطلاعات فروشگاه)
    پوشش کارگاه ۵ (لوگو و فاوآیکون)
    """
    store_name = models.CharField(
        max_length=200,
        default='عطارخونه - فروشگاه تخصصی گیاهان دارویی و سلامت',
        verbose_name='نام فروشگاه (کارگاه ۴)'
    )
    slogan = models.CharField(
        max_length=255,
        default='دانش کهن، سلامت مدرن؛ انتخاب آگاهانه گیاهان دارویی',
        verbose_name='شعار فروشگاه'
    )
    phone = models.CharField(max_length=50, default='021-88997766', verbose_name='تلفن ثابت')
    mobile = models.CharField(max_length=50, default='09123456789', verbose_name='تلفن همراه پشتیبانی')
    email = models.EmailField(default='info@attarkhooneh.ir', verbose_name='رایانامه رسمی فروشگاه')
    province = models.CharField(max_length=100, default='تهران', verbose_name='استان')
    city = models.CharField(max_length=100, default='تهران', verbose_name='شهر')
    address = models.TextField(
        default='تهران، خیابان ولیعصر، بالاتر از تقاطع طالقانی، پلاک ۱۱۴، ساختمان سلامت',
        verbose_name='نشانی فروشگاه'
    )
    postal_code = models.CharField(max_length=20, default='1591613114', verbose_name='کد پستی')
    about_summary = models.TextField(
        default='عطارخونه مرجع تخصصی گیاهان دارویی ارگانیک، دمنوش‌های طبیعی و دستیار هوشمند سلامت با تکیه بر بررسی تداخلات دارویی است.',
        verbose_name='خلاصه درباره ما (فوتر)'
    )
    
    # کارگاه ۵: لوگو و فاوآیکون
    logo = models.ImageField(upload_to='settings/', blank=True, null=True, verbose_name='لوگوی فروشگاه')
    favicon = models.ImageField(upload_to='settings/', blank=True, null=True, verbose_name='فاوآیکون (Favicon)')

    # کارگاه ۳: غیرفعال‌سازی / حالت تعمیرات
    is_maintenance_mode = models.BooleanField(
        default=False,
        verbose_name='حالت تعمیرات فعال است؟ (کارگاه ۳)',
        help_text='در صورت فعال بودن، کاربران عادی پیام تعمیرات را می‌بینند و تنها IPهای مجاز به سایت دسترسی خواهند داشت.'
    )
    maintenance_message = models.TextField(
        default='فروشگاه عطارخونه موقتاً به منظور به‌روزرسانی و ارتقای خدمات در دسترس نیست. به زودی در کنار شما خواهیم بود.',
        verbose_name='متن پیام حالت تعمیرات'
    )
    maintenance_allowed_ips = models.TextField(
        default='127.0.0.1, ::1',
        verbose_name='آی‌پی‌های مجاز کارمندان (کارگاه ۳)',
        help_text='نشانی‌های IP مجاز را با کاما جدا کنید. کارمندان از این IPها به فروشگاه دسترسی کامل خواهند داشت.'
    )

    # هزینه‌های عمومی و تنظیمات سفارش
    gift_wrap_cost = models.PositiveIntegerField(
        default=25000,
        verbose_name='هزینه کادوپیچی سفارش (تومان) - کارگاه ۲۴'
    )
    free_shipping_threshold = models.PositiveIntegerField(
        default=500000,
        verbose_name='حداقل خرید برای ارسال رایگان (تومان)'
    )

    # شبکه‌های اجتماعی (کارگاه ۲۵ و بازارگردانی)
    instagram = models.CharField(max_length=100, default='attarkhooneh_official', blank=True, verbose_name='اینستاگرام')
    telegram = models.CharField(max_length=100, default='attarkhooneh', blank=True, verbose_name='تلگرام')
    eitaa = models.CharField(max_length=100, default='attarkhooneh', blank=True, verbose_name='ایتا')
    bale = models.CharField(max_length=100, default='attarkhooneh', blank=True, verbose_name='بله')

    class Meta:
        verbose_name = 'تنظیمات و اطلاعات فروشگاه'
        verbose_name_plural = 'تنظیمات و اطلاعات فروشگاه (کارگاه ۳، ۴ و ۵)'

    def __str__(self):
        return self.store_name

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj
