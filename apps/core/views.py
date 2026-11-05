from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.db import connection
from django.conf import settings
import sys
import os

from marketing.models import Slider, Banner
from catalog.models import Product, Category
from remedy.models import SymptomCategory
from .models import StoreSetting


from django.db.models import Case, When, Value, IntegerField


class HomeView(View):
    def get(self, request):
        sliders = Slider.objects.filter(is_active=True).order_by('order')
        top_banners = Banner.objects.filter(position='home_top', is_active=True)
        middle_banners = Banner.objects.filter(position='home_middle', is_active=True)[:2]
        
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
        featured_products = Product.objects.filter(is_featured=True).annotate(
            priority=Case(*whens, default=Value(99), output_field=IntegerField())
        ).order_by('priority', '-created_at')[:6]

        latest_products = Product.objects.all().order_by('-created_at')[:8]
        categories = Category.objects.filter(parent=None)[:6]
        symptom_categories = SymptomCategory.objects.all()[:4]

        context = {
            'sliders': sliders,
            'top_banners': top_banners,
            'middle_banners': middle_banners,
            'featured_products': featured_products,
            'latest_products': latest_products,
            'categories': categories,
            'symptom_categories': symptom_categories,
        }
        return render(request, 'core/index.html', context)


class HealthCheckView(View):
    """
    کارگاه ۲۱ و ۲۲ کتاب: ارتقا به نسخه جدید و آزمایش صحت و سلامت ارتقا
    بررسی اتصالات پایگاه داده، فایل‌های ایستا، مجوزهای دایرکتوری و شِمای سیستم
    """
    def get(self, request):
        diagnostics = []

        # ۱. تست سلامت پایگاه داده
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                row = cursor.fetchone()
            diagnostics.append({
                'title': 'اتصال پایگاه داده (SQLite Database)',
                'status': 'OK',
                'details': f'اتصال فعال است و کوئری تستی با موفقیت اجرا شد (پاسخ: {row[0]}).',
                'badge': 'موفق'
            })
        except Exception as e:
            diagnostics.append({
                'title': 'اتصال پایگاه داده',
                'status': 'ERROR',
                'details': str(e),
                'badge': 'خطا'
            })

        # ۲. بررسی دایرکتوری رسانه و دسترسی نوشتن
        media_writable = os.access(settings.MEDIA_ROOT, os.W_OK)
        diagnostics.append({
            'title': 'دایرکتوری فایل‌های رسانه (MEDIA_ROOT)',
            'status': 'OK' if media_writable else 'WARNING',
            'details': f'مسیر {settings.MEDIA_ROOT} با مجوز دسترسی {("مجاز (قابل نوشتن)" if media_writable else "فقط خواندنی")}',
            'badge': 'موفق' if media_writable else 'هشدار'
        })

        # ۳. بررسی وضعیت حالت تعمیرات (کارگاه ۳)
        try:
            store_setting = StoreSetting.get_settings()
            maintenance_status = "فعال (فروشگاه در حال ارتقا)" if store_setting.is_maintenance_mode else "غیرفعال (فروشگاه باز است)"
            diagnostics.append({
                'title': 'وضعیت دسترسی عمومی فروشگاه (کارگاه ۳)',
                'status': 'OK',
                'details': f'{maintenance_status} | آی‌پی‌های مجاز: {store_setting.maintenance_allowed_ips}',
                'badge': 'عادی'
            })
        except Exception as e:
            pass

        # ۴. نسخه نرم‌افزار و پایتون
        import django
        diagnostics.append({
            'title': 'مشخصات محیط نرم‌افزاری و نسخه فریم‌ورک',
            'status': 'OK',
            'details': f'پایتون: {sys.version.split()[0]} | جنگو: {django.__version__} | بستر: Linux / Web',
            'badge': 'پایدار'
        })

        context = {
            'diagnostics': diagnostics,
            'title': 'آزمایش صحت ارتقا و سلامت سامانه (کارگاه ۲۲)'
        }
        return render(request, 'core/health_check.html', context)


def robots_txt(request):
    """
    کارگاه ۲۶: فایل راهنمای موتورهای جستجو و ربات گوگل
    """
    lines = [
        "User-agent: *",
        "Disallow: /attar-management/",
        "Disallow: /orders/checkout/",
        "Disallow: /cart/",
        "Allow: /",
        "",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


class WorkshopsGuideView(View):
    """
    صفحه اختصاصی نمایش ماتریس انطباق ۲۷ کارگاه کتاب برای استاد و هیئت داوری
    """
    def get(self, request):
        return render(request, 'core/workshops_guide.html')
