from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.contrib import messages
from .models import Product, Category, Brand, ProductVariant, ProductFeature, Wishlist


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
            category_ids = [selected_category.id] + list(selected_category.children.values_list('id', flat=True))
            queryset = queryset.filter(category_id__in=category_ids)
        else:
            cat_param = request.GET.get('cat')
            if cat_param:
                matched_cat = Category.objects.filter(slug=cat_param).first()
                if matched_cat:
                    selected_category = matched_cat
                    category_ids = [matched_cat.id] + list(matched_cat.children.values_list('id', flat=True))
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

        total_count = queryset.count()
        paginator = Paginator(queryset, 12)
        page_number = request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            page_obj = paginator.page(1)

        context = {
            'products': page_obj,
            'page_obj': page_obj,
            'products_count': total_count,
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


class WishlistToggleView(View):
    """
    افزودن یا حذف محصول از لیست علاقه‌مندی‌ها با پاسخ ایجکس یا ریدایرکت
    """
    def post(self, request, product_id):
        if not request.user.is_authenticated:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'require_login': True,
                    'message': 'برای نشان کردن کالاها، لطفاً ابتدا وارد حساب کاربری خود شوید.'
                }, status=401)
            messages.info(request, 'برای نشان کردن کالاها، لطفاً وارد حساب خود شوید.')
            return redirect(f'/accounts/login/?next={request.META.get("HTTP_REFERER", "/")}')

        product = get_object_or_404(Product, id=product_id)
        wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()

        if wishlist_item:
            wishlist_item.delete()
            is_added = False
            msg = f'«{product.name}» از لیست علاقه‌مندی‌ها حذف شد.'
        else:
            Wishlist.objects.create(user=request.user, product=product)
            is_added = True
            msg = f'«{product.name}» به لیست علاقه‌مندی‌های شما اضافه شد.'

        total_wishlist = Wishlist.objects.filter(user=request.user).count()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({
                'success': True,
                'is_added': is_added,
                'wishlist_count': total_wishlist,
                'message': msg,
            })

        messages.success(request, msg)
        return redirect(request.META.get('HTTP_REFERER', 'catalog:wishlist'))


class WishlistView(View):
    """
    نمایش کالاهای نشان‌شده و لیست علاقه‌مندی‌های کاربر
    """
    def get(self, request):
        if not request.user.is_authenticated:
            messages.info(request, 'برای مشاهده لیست علاقه‌مندی‌ها، لطفاً وارد شوید.')
            return redirect('/accounts/login/?next=/shop/wishlist/')

        items = Wishlist.objects.filter(user=request.user).select_related('product__category')
        return render(request, 'catalog/wishlist.html', {'wishlist_items': items})
