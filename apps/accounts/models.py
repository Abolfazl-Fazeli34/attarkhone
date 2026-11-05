from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'مدیر کل (Super Admin)'),
        ('accountant', 'حسابدار (Accountant)'),
        ('logistic', 'انباردار و ارسال (Logistics)'),
        ('support', 'کارشناس فروش و پشتیبانی (Sales & Support)'),
        ('customer', 'مشتری عادی (Customer)'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer',
        verbose_name='نقش کاربر / نمایه کارمند',
        help_text='کارگاه ۱ و ۲: تعیین سطوح دسترسی و نمایه‌های کارمندان'
    )
    phone = models.CharField(max_length=15, blank=True, verbose_name='شماره تماس')
    address = models.TextField(blank=True, verbose_name='نشانی پستی')
    postal_code = models.CharField(max_length=10, blank=True, verbose_name='کد پستی')
    national_id = models.CharField(max_length=10, blank=True, verbose_name='کد ملی')

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران و کارمندان (کارگاه ۱ و ۲)'

    @property
    def is_store_staff(self):
        return self.role in ['admin', 'accountant', 'logistic', 'support'] or self.is_staff or self.is_superuser

    @property
    def role_display_fa(self):
        return dict(self.ROLE_CHOICES).get(self.role, 'مشتری')
