from django.db import models
from django.urls import reverse


class StaticPage(models.Model):
    """
    کارگاه ۶: تنظیم محتوای صفحات ایستا (Static CMS)
    مانند شرایط و ضوابط، تماس با ما، روش ارسال، درباره ما
    """
    title = models.CharField(max_length=150, verbose_name="عنوان صفحه")
    slug = models.SlugField(max_length=160, unique=True, allow_unicode=True, verbose_name="نامک صفحه (URL)")
    content = models.TextField(verbose_name="متن و محتوای صفحه (HTML/Text)")
    is_published = models.BooleanField(default=True, verbose_name="منتشر شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ ویرایش")

    class Meta:
        verbose_name = "صفحه ایستا"
        verbose_name_plural = "صفحات ایستا (کارگاه ۶)"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('pages:page_detail', kwargs={'slug': self.slug})


class Article(models.Model):
    """
    بخش مقالات، آموزش‌ها و وبلاگ تندرستی (کارگاه ۶ و ۲۷ - بازاریابی محتوایی و سئو)
    """
    title = models.CharField(max_length=200, verbose_name="عنوان مقاله")
    slug = models.SlugField(max_length=220, unique=True, allow_unicode=True, verbose_name="نامک (Slug)")
    summary = models.TextField(verbose_name="خلاصه و چکیده مقاله")
    content = models.TextField(verbose_name="متن کامل مقاله")
    category = models.CharField(max_length=100, default="طب سنتی و تندرستی", verbose_name="دسته‌بندی موضوعی")
    image = models.CharField(max_length=255, default="/static/img/products/real_tea.jpg", verbose_name="تصویر شاخص مقاله")
    reading_time = models.PositiveIntegerField(default=5, verbose_name="زمان تقریبی مطالعه (دقیقه)")
    views_count = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    
    # اطلاعات علمی و استنادی (دوسیه دفاع علمی کارگاه ۶ و ۲۷)
    author_name = models.CharField(max_length=150, default="دکتر مریم سادات حسینی", verbose_name="نام نویسنده و پژوهشگر")
    author_title = models.CharField(max_length=200, default="متخصص داروسازی سنتی و عضو هیئت علمی", verbose_name="درجه علمی نویسنده")
    scientific_reviewer = models.CharField(max_length=200, default="شورای ارزیابی پژوهشکده گیاهان دارویی دانشگاه تهران", verbose_name="مرجع نظارت و داوری علمی")
    academic_references = models.TextField(
        blank=True,
        default="۱. کتاب قانون در طب، شیخ‌الرئیس ابوعلی سینا، جلد دوم (مفردات ادویه و گیاه‌شناسی بالینی)\n"
                "۲. فارماکوپه گیاهی ایران (Iranian Herbal Pharmacopoeia - IHP)، کمیته تدوین فارماکوپه\n"
                "۳. WHO Monographs on Selected Medicinal Plants, World Health Organization, Geneva\n"
                "۴. Journal of Ethnopharmacology: Phytochemical Profiling, PubMed DOI: 10.1016/j.jep.2021.114389",
        verbose_name="فهرست مراجع دانشگاهی، منابع کهن و کدهای DOI"
    )

    is_published = models.BooleanField(default=True, verbose_name="وضعیت انتشار")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ نگارش")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    class Meta:
        verbose_name = "مقاله و آموزش"
        verbose_name_plural = "مقالات و آموزش‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('pages:article_detail', kwargs={'slug': self.slug})


class ContactMessage(models.Model):
    """
    پیام‌ها، پرسش‌ها و مشاوره‌های ارسالی کاربران از طریق صفحه تماس با ما
    """
    full_name = models.CharField(max_length=150, verbose_name="نام و نام خانوادگی")
    email = models.EmailField(blank=True, verbose_name="نشانی رایانامه")
    phone = models.CharField(max_length=25, verbose_name="شماره تماس")
    subject = models.CharField(max_length=200, blank=True, verbose_name="موضوع پیام")
    message = models.TextField(verbose_name="متن پیام و درخواست مشاوره")
    is_read = models.BooleanField(default=False, verbose_name="بررسی شده توسط پشتیبانی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")

    class Meta:
        verbose_name = "پیام تماس با ما"
        verbose_name_plural = "پیام‌های تماس با ما"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.subject or self.phone}"
