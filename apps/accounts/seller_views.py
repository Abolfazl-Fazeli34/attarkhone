from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.text import slugify
from django.db.models import Sum, Count, F
import uuid
import datetime

from .models import User, SellerProfile
from catalog.models import Product, Category, ProductVariant, Brand, Supplier
from orders.models import Order, OrderItem


class SellerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    محدودسازی دسترسی به پنل فقط برای فروشندگان تاییدشده یا مدیران
    """
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        return user.is_seller or user.is_superuser or user.role == 'admin'

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={self.request.path}')
        messages.warning(self.request, 'برای دسترسی به این بخش، ابتدا باید حساب کاربری فروشنده را فعال نمایید.')
        return redirect('accounts:seller_apply')


class SellerDashboardView(SellerRequiredMixin, View):
    """
    داشبورد مدیریت فروشنده و تأمین‌کننده گیاهان دارویی
    """
    def get(self, request):
        user = request.user
        profile, _ = SellerProfile.objects.get_or_create(
            user=user,
            defaults={
                'store_name': f"مزرعه {user.get_full_name() or user.username}",
                'slug': f"store-{user.username}-{uuid.uuid4().hex[:4]}",
                'is_approved': True
            }
        )

        my_products = Product.objects.filter(seller=user)
        total_products = my_products.count()
        low_stock_products = my_products.filter(stock__lte=10)

        # سفارشات و آمار فروش اقلام این فروشنده
        seller_order_items = OrderItem.objects.filter(product__seller=user).select_related('order', 'product')
        total_sales_count = seller_order_items.aggregate(total=Sum('quantity'))['total'] or 0
        
        # محاسبه درآمد ناخالص فروشنده
        gross_revenue = sum(item.total_price for item in seller_order_items if item.order.is_paid)
        commission = (gross_revenue * profile.commission_percent) // 100
        net_revenue = gross_revenue - commission

        recent_orders = Order.objects.filter(items__product__seller=user).distinct().order_by('-created_at')[:8]

        context = {
            'profile': profile,
            'total_products': total_products,
            'low_stock_products': low_stock_products,
            'total_sales_count': total_sales_count,
            'gross_revenue': gross_revenue,
            'net_revenue': net_revenue,
            'recent_orders': recent_orders,
        }
        return render(request, 'seller/dashboard.html', context)


class SellerProductListView(SellerRequiredMixin, View):
    """
    کاتالوگ محصولات ثبت‌شده توسط این فروشنده
    """
    def get(self, request):
        user = request.user
        products = Product.objects.filter(seller=user).order_by('-created_at')
        q = request.GET.get('q', '').strip()
        if q:
            products = products.filter(name__icontains=q)

        context = {
            'products': products,
            'search_query': q,
        }
        return render(request, 'seller/product_list.html', context)


class SellerProductCreateView(SellerRequiredMixin, View):
    """
    افزودن فرآورده گیاهی یا داروی گیاهی جدید به کاتالوگ فروشنده
    """
    def get(self, request):
        categories = Category.objects.all()
        brands = Brand.objects.all()
        return render(request, 'seller/product_form.html', {
            'categories': categories,
            'brands': brands,
            'is_edit': False,
        })

    def post(self, request):
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category')
        base_price = request.POST.get('base_price', '0').strip()
        discount_percent = request.POST.get('discount_percent', '0').strip()
        stock = request.POST.get('stock', '50').strip()
        
        scientific_name = request.POST.get('scientific_name', '').strip()
        botanical_family = request.POST.get('botanical_family', '').strip()
        harvest_region = request.POST.get('harvest_region', '').strip()
        temperament = request.POST.get('temperament', 'moderate')
        active_compounds = request.POST.get('active_compounds', '').strip()
        brewing_guide = request.POST.get('brewing_guide', '').strip()
        contraindications = request.POST.get('contraindications', '').strip()
        health_license = request.POST.get('health_license', 'سیب سلامت و پروانه ارگانیک ۱۴۰۳/۴۹۸۲۱').strip()
        short_description = request.POST.get('short_description', '').strip()
        description = request.POST.get('description', '').strip()

        if not name or not category_id or not base_price:
            messages.error(request, 'نام محصول، دسته‌بندی و قیمت پایه الزامی هستند.')
            return redirect('accounts:seller_product_add')

        category = get_object_or_404(Category, id=category_id)
        
        # تولید اسلاگ یکتا
        unique_slug = slugify(name, allow_unicode=True) or f"prod-{uuid.uuid4().hex[:6]}"
        if Product.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{unique_slug}-{uuid.uuid4().hex[:4]}"

        image = request.FILES.get('image')

        product = Product.objects.create(
            seller=request.user,
            name=name,
            slug=unique_slug,
            category=category,
            base_price=int(base_price),
            discount_percent=int(discount_percent or 0),
            stock=int(stock or 50),
            scientific_name=scientific_name,
            botanical_family=botanical_family,
            harvest_region=harvest_region,
            temperament=temperament,
            active_compounds=active_compounds,
            brewing_guide=brewing_guide,
            contraindications=contraindications,
            health_license=health_license,
            short_description=short_description or name,
            description=description or name,
            image=image,
            is_organic=True,
            is_featured=False
        )

        # ایجاد ۳ مشخصه وزنی استاندارد جهت راحتی انتخاب خریدار (کارگاه ۱۳)
        bp = product.final_price
        ProductVariant.objects.create(
            product=product,
            weight_label="۵۰ گرم",
            grind_type="درسته و سورت‌شده",
            price=max(10000, (bp * 55) // 100),
            stock=product.stock // 2 or 10,
            sku=f"SKU-{product.id}-50G"
        )
        ProductVariant.objects.create(
            product=product,
            weight_label="۱۰۰ گرم",
            grind_type="درسته و سورت‌شده",
            price=bp,
            stock=product.stock,
            sku=f"SKU-{product.id}-100G"
        )
        ProductVariant.objects.create(
            product=product,
            weight_label="۲۵۰ گرم (اقتصادی)",
            grind_type="درسته و سورت‌شده",
            price=max(20000, (bp * 230) // 100),
            stock=product.stock // 3 or 5,
            sku=f"SKU-{product.id}-250G"
        )

        messages.success(request, f'محصول گیاهی «{product.name}» با موفقیت افزوده و بارکد QR اختصاصی آن صادر شد.')
        return redirect('accounts:seller_products')


class SellerProductUpdateView(SellerRequiredMixin, View):
    """
    ویرایش اطلاعات و موجودی کالا توسط فروشنده
    """
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, seller=request.user)
        categories = Category.objects.all()
        return render(request, 'seller/product_form.html', {
            'product': product,
            'categories': categories,
            'is_edit': True,
        })

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, seller=request.user)
        
        product.name = request.POST.get('name', product.name).strip()
        cat_id = request.POST.get('category')
        if cat_id:
            product.category = get_object_or_404(Category, id=cat_id)

        product.base_price = int(request.POST.get('base_price', product.base_price))
        product.discount_percent = int(request.POST.get('discount_percent', product.discount_percent))
        product.stock = int(request.POST.get('stock', product.stock))
        
        product.scientific_name = request.POST.get('scientific_name', product.scientific_name).strip()
        product.botanical_family = request.POST.get('botanical_family', product.botanical_family).strip()
        product.harvest_region = request.POST.get('harvest_region', product.harvest_region).strip()
        product.temperament = request.POST.get('temperament', product.temperament)
        product.active_compounds = request.POST.get('active_compounds', product.active_compounds).strip()
        product.brewing_guide = request.POST.get('brewing_guide', product.brewing_guide).strip()
        product.contraindications = request.POST.get('contraindications', product.contraindications).strip()
        product.health_license = request.POST.get('health_license', product.health_license).strip()
        product.short_description = request.POST.get('short_description', product.short_description).strip()
        product.description = request.POST.get('description', product.description).strip()

        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()
        messages.success(request, f'مشخصات محصول «{product.name}» با موفقیت به‌روزرسانی شد.')
        return redirect('accounts:seller_products')


class SellerProductDeleteView(SellerRequiredMixin, View):
    """
    حذف محصول توسط فروشنده
    """
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, seller=request.user)
        name = product.name
        product.delete()
        messages.info(request, f'محصول «{name}» از کاتالوگ فروشگاه شما حذف گردید.')
        return redirect('accounts:seller_products')


class SellerProductQRView(SellerRequiredMixin, View):
    """
    صدور و چاپ برچسب شناسنامه کالا به همراه بارکد QR Code و برگه کنترل کیفیت
    """
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, seller=request.user)
        qr_data_uri = product.get_qr_code_data_uri(request=request)
        batch_no = f"ATK-1403-B{product.id:04d}"
        
        context = {
            'product': product,
            'qr_data_uri': qr_data_uri,
            'batch_no': batch_no,
            'pack_date': datetime.date.today(),
            'expiry_date': datetime.date.today() + datetime.timedelta(days=730),
        }
        return render(request, 'seller/product_qr_label.html', context)


class SellerOrdersView(SellerRequiredMixin, View):
    """
    سفارش‌های مرتبط با محصولات این فروشنده
    """
    def get(self, request):
        user = request.user
        orders = Order.objects.filter(items__product__seller=user).distinct().order_by('-created_at')
        return render(request, 'seller/orders.html', {'orders': orders})


class SellerSettingsView(SellerRequiredMixin, View):
    """
    تنظیمات حساب فروشگاه و شماره شبا جهت تسویه
    """
    def get(self, request):
        profile, _ = SellerProfile.objects.get_or_create(user=request.user)
        return render(request, 'seller/settings.html', {'profile': profile})

    def post(self, request):
        profile, _ = SellerProfile.objects.get_or_create(user=request.user)
        profile.store_name = request.POST.get('store_name', profile.store_name).strip()
        profile.national_id_or_registration = request.POST.get('national_id_or_registration', profile.national_id_or_registration).strip()
        profile.shaba_number = request.POST.get('shaba_number', profile.shaba_number).strip()
        profile.phone_work = request.POST.get('phone_work', profile.phone_work).strip()
        profile.address = request.POST.get('address', profile.address).strip()
        profile.description = request.POST.get('description', profile.description).strip()

        if 'logo' in request.FILES:
            profile.logo = request.FILES['logo']

        profile.save()
        messages.success(request, 'تنظیمات فروشگاه و حساب بانکی شما با موفقیت ذخیره شد.')
        return redirect('accounts:seller_settings')


class SellerApplyView(LoginRequiredMixin, View):
    """
    ثبت‌نام و درخواست فعال‌سازی پنل فروشندگی برای کاربران عادی
    """
    def get(self, request):
        if request.user.is_seller:
            return redirect('accounts:seller_dashboard')
        return render(request, 'seller/apply.html')

    def post(self, request):
        user = request.user
        store_name = request.POST.get('store_name', '').strip()
        national_id = request.POST.get('national_id', '').strip()
        shaba_number = request.POST.get('shaba_number', '').strip()
        address = request.POST.get('address', '').strip()
        phone_work = request.POST.get('phone_work', '').strip()
        description = request.POST.get('description', '').strip()

        if not store_name or not national_id or not shaba_number:
            messages.error(request, 'تکمیل نام فروشگاه/مزرعه، کد ملی و شماره شبا الزامی است.')
            return render(request, 'seller/apply.html')

        user.role = 'seller'
        user.save(update_fields=['role'])

        slug = slugify(store_name, allow_unicode=True) or f"store-{user.id}"
        if SellerProfile.objects.filter(slug=slug).exists():
            slug = f"{slug}-{uuid.uuid4().hex[:4]}"

        SellerProfile.objects.create(
            user=user,
            store_name=store_name,
            slug=slug,
            national_id_or_registration=national_id,
            shaba_number=shaba_number,
            phone_work=phone_work or user.phone,
            address=address,
            description=description,
            is_approved=True
        )

        messages.success(request, 'به خانواده تأمین‌کنندگان عطارخونه خوش آمدید! پنل فروشندگی شما با موفقیت فعال گردید.')
        return redirect('accounts:seller_dashboard')


class SellerProductToggleStockView(SellerRequiredMixin, View):
    """
    تغییر سریع وضعیت موجودی انبار توسط فروشنده (موجود / ناموجود)
    """
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, seller=request.user)
        if product.stock > 0:
            product.stock = 0
            is_in_stock = False
            msg = f"موجودی «{product.name}» به ناموجود تغییر یافت."
        else:
            product.stock = 50
            is_in_stock = True
            msg = f"موجودی «{product.name}» به تعداد ۵۰ بسته شارژ گردید."
        product.save(update_fields=['stock'])

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'in_stock': is_in_stock,
                'stock': product.stock,
                'message': msg,
            })

        messages.success(request, msg)
        return redirect('accounts:seller_products')
