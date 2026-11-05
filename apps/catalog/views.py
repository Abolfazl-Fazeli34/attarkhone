from django.shortcuts import render, get_object_or_404
from django.views import View
from django.db.models import Q
from .models import Product, Category, Brand, ProductVariant, ProductFeature


class ProductListView(View):
    """
    کارگاه ۱۸: پیکربندی ماژول جستجوی لایه‌ای (Faceted Search)
    فیلتر همزمان بر اساس شاخه، طبع، برند، قیمت، ارگانیک بودن و جستجوی متنی
    """
    def get(self, request, category_slug=None):
        queryset = Product.objects.all().select_related('category', 'brand')
        selected_category = None

        # فیلتر شاخه (دسته‌بندی)
        if category_slug:
            selected_category = get_object_or_404(Category, slug=category_slug)
            # نمایش محصولات این شاخه و زیرشاخه‌های آن
            category_ids = [selected_category.id] + list(selected_category.children.values_list('id', flat=True))
            queryset = queryset.filter(category_id__in=category_ids)

        # جستجوی متنی (کارگاه ۱۸ و ۲۷)
        q = request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) |
                Q(short_description__icontains=q) |
                Q(description__icontains=q) |
                Q(meta_keywords__icontains=q)
            )

        # فیلتر طبع و مزاج گیاه (ویژگی اختصاصی عطارخونه)
        temperament = request.GET.get('temperament')
        if temperament:
            queryset = queryset.filter(temperament=temperament)

        # فیلتر برند (کارگاه ۱۵)
        brand_id = request.GET.get('brand')
        if brand_id and brand_id.isdigit():
            queryset = queryset.filter(brand_id=int(brand_id))

        # فیلتر ارگانیک
        is_organic = request.GET.get('organic')
        if is_organic == '1':
            queryset = queryset.filter(is_organic=True)

        # فیلتر محدوده قیمت (تومان)
        min_price = request.GET.get('min_price')
        if min_price and min_price.isdigit():
            queryset = queryset.filter(base_price__gte=int(min_price))

        max_price = request.GET.get('max_price')
        if max_price and max_price.isdigit():
            queryset = queryset.filter(base_price__lte=int(max_price))

        # مرتب‌سازی
        sort = request.GET.get('sort', 'popular')
        if sort == 'price_asc':
            queryset = queryset.order_by('base_price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-base_price')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        else:
            # پیش‌فرض و محبوب‌ترین: اولویت با اقلام اصلی موکاپ
            from django.db.models import Case, When, Value, IntegerField
            priority_slugs = [
                'green-tea-organic',
                'gol-gavzaban-momtaz',
                'damnoosh-aramesh-bakhsh',
                'health-gift-box',
                'black-seed-oil-pure',
                'darchin-asl',
                'zaferan-asl-irani',
                'gol-mohammadi-daraje-yek',
            ]
            whens = [When(slug=s, then=Value(i)) for i, s in enumerate(priority_slugs)]
            queryset = queryset.annotate(
                priority=Case(*whens, default=Value(99), output_field=IntegerField())
            ).order_by('priority', '-sales_count', '-created_at')

        categories = Category.objects.filter(parent=None)
        brands = Brand.objects.all()

        context = {
            'products': queryset,
            'products_count': queryset.count(),
            'categories': categories,
            'selected_category': selected_category,
            'brands': brands,
            'temperament_choices': Product.TEMPERAMENT_CHOICES,
            'current_temperament': temperament,
            'current_brand': int(brand_id) if brand_id and brand_id.isdigit() else None,
            'current_sort': sort,
            'search_query': q,
            'min_price': min_price or '',
            'max_price': max_price or '',
            'is_organic': is_organic == '1',
        }
        return render(request, 'catalog/product_list.html', context)


class ProductDetailView(View):
    """
    صفحه تکی محصول
    کارگاه ۱۳ (مشخصه‌ها - انتخاب وزن)، کارگاه ۱۴ (ویژگی‌ها - خواص و طبع)
    کارگاه ۲۶ و ۲۷ (سئو، کلمات کلیدی، ساختار Schema.org)
    """
    def get(self, request, slug):
        product = get_object_or_404(
            Product.objects.select_related('category', 'brand', 'supplier').prefetch_related('variants', 'features'),
            slug=slug
        )
        related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

        context = {
            'product': product,
            'variants': product.variants.all(),
            'features': product.features.all(),
            'related_products': related_products,
        }
        return render(request, 'catalog/product_detail.html', context)
