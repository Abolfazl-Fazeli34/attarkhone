from django.db import models
from django.urls import reverse
from django.conf import settings


class Category(models.Model):
    """
    کارگاه ۱۱: افزودن شاخه جدید به همراه امکان شاخه‌های والد و فرزند (تودرتو)
    """
    name = models.CharField(max_length=150, verbose_name="نام شاخه")
    slug = models.SlugField(max_length=160, unique=True, allow_unicode=True, verbose_name="نامک (Slug)")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="شاخه والد (کارگاه ۱۱)"
    )
    description = models.TextField(blank=True, verbose_name="توضیحات شاخه")
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name="تصویر شاخه")
    icon = models.CharField(max_length=50, default='leaf', blank=True, verbose_name="نام آیکون")
    
    # کارگاه ۲۶ و ۲۷: سئو
    meta_title = models.CharField(max_length=150, blank=True, verbose_name="عنوان متا (SEO)")
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name="کلمات کلیدی KWFinder")
    meta_description = models.TextField(blank=True, verbose_name="توضیحات متا (SEO)")

    class Meta:
        verbose_name = "شاخه و دسته‌بندی"
        verbose_name_plural = "شاخه‌ها و دسته‌بندی‌ها (کارگاه ۱۱)"
        ordering = ['name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} » {self.name}"
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_list_by_category', kwargs={'category_slug': self.slug})


class Brand(models.Model):
    """
    کارگاه ۱۵: افزودن برند و شرکت‌های تولیدکننده
    """
    name = models.CharField(max_length=120, verbose_name="نام برند / تولیدکننده")
    slug = models.SlugField(max_length=130, unique=True, allow_unicode=True, verbose_name="نامک")
    description = models.TextField(blank=True, verbose_name="توضیحات برند")
    logo = models.ImageField(upload_to='brands/', null=True, blank=True, verbose_name="لوگوی برند")
    website = models.URLField(blank=True, verbose_name="تارنمای برند")

    class Meta:
        verbose_name = "برند و تولیدکننده"
        verbose_name_plural = "برندها و تولیدکنندگان (کارگاه ۱۵)"

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """
    کارگاه ۱۶: افزودن تأمین‌کننده
    """
    name = models.CharField(max_length=150, verbose_name="نام تأمین‌کننده / مزرعه طرف قرارداد")
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="شخص رابط")
    phone = models.CharField(max_length=30, blank=True, verbose_name="تلفن تماس")
    address = models.TextField(blank=True, verbose_name="آدرس مزارع / انبار تأمین‌کننده")

    class Meta:
        verbose_name = "تأمین‌کننده"
        verbose_name_plural = "تأمین‌کنندگان (کارگاه ۱۶)"

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    مدیریت محصولات فروشگاه عطارخونه
    پوشش کارگاه‌های ۱۳، ۱۴، ۱۸، ۲۵، ۲۶ و ۲۷
    """
    TEMPERAMENT_CHOICES = [
        ('hot_dry', 'گرم و خشک (صفراوی)'),
        ('hot_wet', 'گرم و تر (دموی)'),
        ('cold_dry', 'سرد و خشک (سوداوی)'),
        ('cold_wet', 'سرد و تر (بلغمی)'),
        ('moderate', 'معتدل'),
    ]

    name = models.CharField(max_length=200, verbose_name="نام محصول")
    slug = models.SlugField(max_length=220, unique=True, allow_unicode=True, verbose_name="نامک")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="شاخه محصول (کارگاه ۱۱)"
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="برند (کارگاه ۱۵)"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="تأمین‌کننده (کارگاه ۱۶)"
    )
    temperament = models.CharField(
        max_length=20,
        choices=TEMPERAMENT_CHOICES,
        default='moderate',
        verbose_name="طبع و مزاج گیاه (کارگاه ۱۴)"
    )
    base_price = models.PositiveIntegerField(verbose_name="قیمت پایه (تومان)")
    discount_percent = models.PositiveIntegerField(default=0, verbose_name="تخفیف ویژه کالا (درصد)")
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="تصویر شاخص")
    short_description = models.CharField(max_length=350, verbose_name="توضیح کوتاه")
    description = models.TextField(verbose_name="توضیحات کامل خواص و راهنما")
    
    # مشخصات تکمیلی گیاه‌شناسی و درمانی (High-Detail Clinical & Botanical Specs)
    scientific_name = models.CharField(max_length=150, blank=True, verbose_name="نام علمی گیاه‌شناسی (لاتین)")
    botanical_family = models.CharField(max_length=100, blank=True, verbose_name="خانواده و تیره گیاهی")
    harvest_region = models.CharField(max_length=150, blank=True, verbose_name="خاستگاه و منطقه برداشت اقلیمی")
    active_compounds = models.CharField(max_length=255, blank=True, verbose_name="ترکیبات موثره دارویی و فیتوشیمیایی")
    traditional_temperament_degree = models.CharField(max_length=120, blank=True, verbose_name="طبع و مصلح سنتی تخصصی")
    organ_benefits = models.TextField(blank=True, verbose_name="خواص درمانی تفکیکی اندام‌ها")
    brewing_guide = models.TextField(blank=True, verbose_name="پروتکل دم‌آوری و نحوه مصرف اصولی")
    contraindications = models.TextField(blank=True, verbose_name="تداخلات دارویی و هشدارهای بالینی")
    health_license = models.CharField(max_length=100, blank=True, default="سیب سلامت و گواهی ارگانیک ۱۴۰۳/۴۹۸۲۱", verbose_name="شماره پروانه بهداشت و سیب سلامت")
    storage_conditions = models.CharField(max_length=200, blank=True, default="در جای خشک، خنک و دور از تابش مستقیم آفتاب نگهداری شود", verbose_name="شرایط نگهداری و انبارش")

    is_organic = models.BooleanField(default=True, verbose_name="دارای گواهی ارگانیک و بهداشت")
    is_featured = models.BooleanField(default=False, verbose_name="نمایش در محصولات منتخب صفحه اول")
    is_eco_packaging = models.BooleanField(default=True, verbose_name="بسته‌بندی پاکت زیپ‌کیپ قابل بازیافت")
    
    stock = models.PositiveIntegerField(default=50, verbose_name="موجودی انبار")
    sales_count = models.PositiveIntegerField(default=0, verbose_name="تعداد فروش")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    # کارگاه ۲۶ و ۲۷: سئو و کلمات کلیدی KWFinder
    meta_title = models.CharField(max_length=150, blank=True, verbose_name="عنوان متا برای گوگل")
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name="کلمات کلیدی تحقیق‌شده با KWFinder")
    meta_description = models.TextField(blank=True, verbose_name="توضیحات متای سئو")

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات (کاتالوگ)"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def get_display_image(self):
        if self.image:
            return self.image.url
        slug = self.slug.lower()
        if 'damnoosh' in slug or 'aramesh' in slug or 'relax' in slug:
            return '/static/img/products/real_jar.jpg'
        elif 'gavzaban' in slug:
            return '/static/img/products/real_herb.jpg'
        elif 'green-tea' in slug or 'tea' in slug:
            return '/static/img/products/real_tea.jpg'
        elif 'box' in slug or 'package' in slug or 'gift' in slug:
            return '/static/img/products/real_box.jpg'
        elif 'oil' in slug or 'roghan' in slug or 'black-seed' in slug:
            return '/static/img/categories/cat_oils.jpg'
        elif 'darchin' in slug or 'cinnamon' in slug or 'spice' in slug:
            return '/static/img/categories/cat_spices.jpg'
        elif 'ostokhoddos' in slug or 'lavender' in slug or 'wellness' in slug:
            return '/static/img/categories/cat_wellness.jpg'
        elif 'zaferan' in slug or 'saffron' in slug:
            return '/static/img/products/prod_saffron.jpg'
        elif 'gol-mohammadi' in slug or 'rose' in slug or 'damascena' in slug:
            return '/static/img/products/prod_rose.jpg'
        elif 'baboneh' in slug or 'chamomile' in slug:
            return '/static/img/products/prod_chamomile.jpg'
        elif 'nana' in slug or 'mint' in slug or 'peppermint' in slug:
            return '/static/img/products/prod_mint.jpg'
        elif 'kasni' in slug or 'aragh' in slug:
            return '/static/img/categories/cat_tea.jpg'
        return '/static/img/products/real_jar.jpg'

    @property
    def final_price(self):
        if self.discount_percent > 0:
            discount = (self.base_price * self.discount_percent) // 100
            return self.base_price - discount
        return self.base_price

    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={'slug': self.slug})


class ProductVariant(models.Model):
    """
    کارگاه ۱۳: تعریف مشخصه‌ها (Attributes)
    انتخاب مشخصه توسط خریدار (مانند وزن یا نوع بسته) که قیمت و موجودی را تغییر می‌دهد
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name="محصول")
    weight_label = models.CharField(max_length=50, verbose_name="مشخصه وزن/اندازه (مثلاً ۱۰۰ گرم)")
    grind_type = models.CharField(
        max_length=50,
        default='درسته و سورت‌شده',
        verbose_name="مشخصه آسیاب / فرآوری"
    )
    price = models.PositiveIntegerField(verbose_name="قیمت این مشخصه (تومان)")
    stock = models.PositiveIntegerField(default=20, verbose_name="موجودی این مشخصه")
    sku = models.CharField(max_length=50, blank=True, verbose_name="شناسه کالا (SKU)")

    class Meta:
        verbose_name = "مشخصه محصول (Attribute)"
        verbose_name_plural = "مشخصه‌های محصولات (کارگاه ۱۳)"

    def __str__(self):
        return f"{self.product.name} - {self.weight_label} ({self.grind_type})"


class ProductFeature(models.Model):
    """
    کارگاه ۱۴: تعریف ویژگی‌ها (Features)
    مشخصات فنی و خواص ثابت گیاه جهت آگاهی مشتری و فیلترهای جستجو
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='features', verbose_name="محصول")
    name = models.CharField(
        max_length=100,
        verbose_name="نام ویژگی (مثلاً اندام مصرفی، مصلح، دوز استاندارد، میزان اسانس)"
    )
    value = models.CharField(
        max_length=200,
        verbose_name="مقدار ویژگی (مثلاً گل‌آذین خشک، عسل طبیعی، ۲.۱ درصد)"
    )

    class Meta:
        verbose_name = "ویژگی محصول (Feature)"
        verbose_name_plural = "ویژگی‌های محصولات (کارگاه ۱۴)"

    def __str__(self):
        return f"{self.product.name} | {self.name}: {self.value}"


class Wishlist(models.Model):
    """
    لیست علاقه‌مندی‌ها و کالاهای نشان‌شده کاربر
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlists', verbose_name="کاربر")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by', verbose_name="محصول")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = "علاقه‌مندی"
        verbose_name_plural = "لیست علاقه‌مندی‌ها"

    def __str__(self):
        return f"{self.user} - {self.product.name}"
