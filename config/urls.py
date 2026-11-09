from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse

from core.sitemaps import ProductSitemap, CategorySitemap, PageSitemap
from core.views import HealthCheckView

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
    # پنل ادمین رسمی پیش‌فرض جنگو
    path('admin/', admin.site.urls),

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
    path('health/', lambda r: HttpResponse('OK', content_type='text/plain'), name='health'),
    path('cart/', RedirectView.as_view(url='/orders/cart/', permanent=False)),
    path('checkout/', RedirectView.as_view(url='/orders/checkout/', permanent=False)),
    path('articles/', RedirectView.as_view(url='/pages/articles/', permanent=False)),

    # سئو و نقشه سایت (کارگاه ۲۶)
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

from django.views.static import serve
from django.urls import re_path

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
