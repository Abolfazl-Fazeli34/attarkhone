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
