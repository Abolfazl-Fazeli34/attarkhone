from django.db import models
from catalog.models import Product


class SymptomCategory(models.Model):
    """
    دسته‌بندی‌های عارضه‌یاب تندرستی
    """
    title = models.CharField(max_length=150, verbose_name="عنوان عارضه / هدف سلامتی")
    slug = models.SlugField(max_length=160, unique=True, allow_unicode=True)
    icon = models.CharField(max_length=50, default='heart', verbose_name="آیکون")
    description = models.TextField(verbose_name="توضیح علائم شایع")

    class Meta:
        verbose_name = "دسته علائم عارضه‌یاب"
        verbose_name_plural = "دسته‌های علائم عارضه‌یاب"

    def __str__(self):
        return self.title


class ChemicalDrug(models.Model):
    """
    بانک اطلاعات داروهای شیمیایی جهت بررسی تداخل
    """
    name = models.CharField(max_length=150, verbose_name="نام داروی شیمیایی (فارسی و انگلیسی)")
    category = models.CharField(max_length=100, verbose_name="دسته دارویی (مثلاً رقیق‌کننده خون، ضدفشار، ضددیابت)")
    description = models.TextField(blank=True, verbose_name="توضیحات عملکرد دارو")

    class Meta:
        verbose_name = "داروی شیمیایی"
        verbose_name_plural = "بانک داروهای شیمیایی جهت بررسی تداخلات"

    def __str__(self):
        return f"{self.name} ({self.category})"


class DrugInteraction(models.Model):
    """
    قوانین تداخل داروی شیمیایی با گیاه دارویی
    """
    SEVERITY_CHOICES = [
        ('danger', 'خطرناک و ممنوع (خطر عوارض جدی بالینی)'),
        ('warning', 'هشدار و احتیاط (نیاز به فاصله زمانی یا مشورت پزشک)'),
        ('safe', 'ایمن و بدون تداخل اثبات‌شده'),
    ]

    drug = models.ForeignKey(ChemicalDrug, on_delete=models.CASCADE, related_name='interactions', verbose_name="داروی شیمیایی")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='drug_interactions', verbose_name="گیاه دارویی در فروشگاه")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='warning', verbose_name="شدت تداخل")
    warning_text = models.TextField(verbose_name="متن هشدار تخصصی به خریدار")

    class Meta:
        verbose_name = "قانون تداخل دارو و گیاه"
        verbose_name_plural = "قوانین تداخل دارو و گیاه (Interaction Rules)"

    def __str__(self):
        return f"تداخل {self.drug.name} با {self.product.name} ({self.get_severity_display()})"


class HealthRemedyPackage(models.Model):
    """
    پکیج‌های پیشنهادی سیستم عارضه‌یاب
    """
    category = models.ForeignKey(SymptomCategory, on_delete=models.CASCADE, related_name='packages', verbose_name="دسته عارضه")
    title = models.CharField(max_length=200, verbose_name="عنوان پکیج درمانی-گیاهی")
    description = models.TextField(verbose_name="علت و خواص ترکیبی این نسخه")
    usage_guide = models.TextField(verbose_name="دستور و زمان‌بندی مصرف روزانه")
    products = models.ManyToManyField(Product, related_name='remedy_packages', verbose_name="گیاهان و دمنوش‌های موجود در پکیج")
    discounted_package_price = models.PositiveIntegerField(verbose_name="قیمت کل پکیج با تخفیف ویژه (تومان)")

    class Meta:
        verbose_name = "پکیج پیشنهادی عارضه‌یاب"
        verbose_name_plural = "پکیج‌های پیشنهادی عارضه‌یاب"

    def __str__(self):
        return self.title


class ConsultationBooking(models.Model):
    """
    سامانه رزرو نوبت مشاوره تخصصی رایگان با متخصصان و پزشکان طب سنتی
    (پیاده‌سازی دکمه طلایی هیرو بنر صفحه اول و مدل درآمدی BMC گزارش پروژه)
    """
    STATUS_CHOICES = [
        ('pending', 'در انتظار تماس کارشناس'),
        ('contacted', 'تماس گرفته شد / در حال پیگیری'),
        ('completed', 'مشاوره با موفقیت انجام شد'),
        ('cancelled', 'لغو شده'),
    ]

    name = models.CharField(max_length=150, verbose_name="نام و نام خانوادگی متقاضی")
    phone = models.CharField(max_length=20, verbose_name="شماره تماس جهت مشاوره")
    symptom_category = models.CharField(max_length=100, default="مشاوره عمومی تندرستی", verbose_name="موضوع و زمینه مشاوره")
    preferred_time = models.CharField(max_length=50, default="صبح (۹ الی ۱۳)", verbose_name="زمان پیشنهادی تماس")
    notes = models.TextField(blank=True, verbose_name="شرح مشکل یا بیماری زمینه‌ای")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت بررسی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت درخواست")

    class Meta:
        verbose_name = "درخواست مشاوره تخصصی"
        verbose_name_plural = "درخواست‌های مشاوره سلامت (کارگاه ۱ و ۲)"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.phone}) - {self.symptom_category}"
