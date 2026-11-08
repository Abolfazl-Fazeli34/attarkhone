from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings
import random
import datetime


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'مدیر کل (Super Admin)'),
        ('accountant', 'حسابدار (Accountant)'),
        ('logistic', 'انباردار و ارسال (Logistics)'),
        ('support', 'کارشناس فروش و پشتیبانی (Sales & Support)'),
        ('seller', 'فروشنده و تأمین‌کننده (Vendor/Seller)'),
        ('customer', 'مشتری عادی (Customer)'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer',
        verbose_name='نقش کاربر / نمایه کارمند',
        help_text='کارگاه ۱ و ۲: تعیین سطوح دسترسی و نمایه‌های کارمندان و فروشندگان'
    )
    phone = models.CharField(max_length=15, blank=True, verbose_name='شماره تماس')
    address = models.TextField(blank=True, verbose_name='نشانی پستی')
    postal_code = models.CharField(max_length=10, blank=True, verbose_name='کد پستی')
    national_id = models.CharField(max_length=10, blank=True, verbose_name='کد ملی')
    email_verified = models.BooleanField(default=False, verbose_name='رایانامه تایید شده با کد OTP')

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران، کارمندان و فروشندگان (کارگاه ۱ و ۲)'

    @property
    def is_store_staff(self):
        return self.role in ['admin', 'accountant', 'logistic', 'support'] or self.is_staff or self.is_superuser

    @property
    def is_seller(self):
        return self.role == 'seller' or hasattr(self, 'seller_profile')

    @property
    def role_display_fa(self):
        return dict(self.ROLE_CHOICES).get(self.role, 'مشتری')


class SellerProfile(models.Model):
    """
    پروفایل اختصاصی تأمین‌کننده و فروشنده گیاهان دارویی
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_profile',
        verbose_name='کاربر متصل'
    )
    store_name = models.CharField(max_length=150, verbose_name='نام فروشگاه / مزرعه کشت')
    slug = models.SlugField(max_length=160, unique=True, allow_unicode=True, verbose_name='نامک اختصاصی (URL)')
    national_id_or_registration = models.CharField(max_length=50, blank=True, verbose_name='کد ملی یا شماره ثبت صنفی')
    shaba_number = models.CharField(max_length=30, blank=True, verbose_name='شماره شبا جهت تسویه (بدون IR یا با IR)')
    phone_work = models.CharField(max_length=30, blank=True, verbose_name='تلفن ثابت یا همراه کاری')
    address = models.TextField(blank=True, verbose_name='نشانی مزرعه یا انبار بسته‌بندی')
    description = models.TextField(blank=True, verbose_name='معرفی مزرعه، استانداردها و تجارب کشت ارگانیک')
    logo = models.ImageField(upload_to='sellers/logos/', null=True, blank=True, verbose_name='لوگوی مزرعه/فروشگاه')
    banner = models.ImageField(upload_to='sellers/banners/', null=True, blank=True, verbose_name='تصویر هدر فروشگاه')
    is_approved = models.BooleanField(default=True, verbose_name='تایید صلاحیت توسط مدیر پلتفرم')
    commission_percent = models.PositiveIntegerField(default=10, verbose_name='درصد کارمزد پلتفرم')
    wallet_balance = models.PositiveIntegerField(default=0, verbose_name='موجودی کیف پول (تومان)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ عضویت فروشنده')

    class Meta:
        verbose_name = 'پروفایل فروشنده'
        verbose_name_plural = 'پروفایل‌های فروشندگان و تأمین‌کنندگان'

    def __str__(self):
        return f"{self.store_name} ({self.user.get_full_name() or self.user.username})"


class EmailOTP(models.Model):
    """
    کدهای یکبار مصرف اعتبارسنجی ارسال‌شده به ایمیل خریداران و فروشندگان
    """
    PURPOSE_CHOICES = [
        ('register', 'فعال‌سازی و تکمیل ثبت‌نام'),
        ('login', 'ورود بدون رمز عبور (OTP Login)'),
        ('reset', 'بازیابی رمز عبور'),
    ]

    email = models.EmailField(verbose_name='نشانی ایمیل')
    code = models.CharField(max_length=6, verbose_name='کد تایید ۵ رقمی')
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='register', verbose_name='هدف کد')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ایجاد')
    expires_at = models.DateTimeField(verbose_name='زمان انقضا')
    is_used = models.BooleanField(default=False, verbose_name='استفاده شده')

    class Meta:
        verbose_name = 'کد تایید رایانامه (OTP)'
        verbose_name_plural = 'کدهای تایید رایانامه (OTP)'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} - {self.code} ({self.purpose})"

    @property
    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    @classmethod
    def generate_code(cls, email, purpose='register', ttl_minutes=5):
        # باطل کردن کدهای قبلی استفاده‌نشده برای این ایمیل و هدف
        cls.objects.filter(email__iexact=email, purpose=purpose, is_used=False).update(is_used=True)
        code_str = str(random.randint(10000, 99999))
        expires = timezone.now() + datetime.timedelta(minutes=ttl_minutes)
        return cls.objects.create(
            email=email.strip().lower(),
            code=code_str,
            purpose=purpose,
            expires_at=expires,
            is_used=False
        )
