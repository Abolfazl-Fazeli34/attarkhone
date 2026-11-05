from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from core.sitemaps import ProductSitemap, CategorySitemap, PageSitemap

# کارگاه ۲۶: نقشه سایت (sitemap.xml)
sitemaps = {
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'pages': PageSitemap,
}

# تغییر عنوان‌های پنل ادمین متناسب با عطارخونه و پودمان ۲
admin.site.site_header = "سامانه مدیریت جامع عطارخونه (پودمان ۲)"
admin.site.site_title = "پنل مدیریت عطارخونه"
admin.site.index_title = "میز کار و داشبورد مدیریت فروشگاه الکترونیکی"

urlpatterns = [
    # ص ۱۱۳ کتاب درسی: تغییر آدرس پیش‌فرض ادمین به نشانی غیرقابل حدس جهت افزایش امنیت
    path('attar-management/', admin.site.urls),

    # اپلیکیشن‌های اصلی پروژه
    path('', include('core.urls', namespace='core')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('shop/', include('catalog.urls', namespace='catalog')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('remedy/', include('remedy.urls', namespace='remedy')),

    # میانبرهای کاربردی جهت دسترسی سریع
    path('cart/', RedirectView.as_view(url='/orders/cart/', permanent=False)),
    path('checkout/', RedirectView.as_view(url='/orders/checkout/', permanent=False)),

    # سئو و نقشه سایت (کارگاه ۲۶)
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
