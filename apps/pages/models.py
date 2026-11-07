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
