import urllib.parse
from django.shortcuts import render
from django.conf import settings
from django.middleware.csrf import CsrfViewMiddleware
from django.http.request import is_same_domain
from .models import StoreSetting


class AttarCsrfViewMiddleware(CsrfViewMiddleware):
    """
    پشتیبانی کامل و تضمین‌شده از بررسی CSRF در محیط‌های لوکال، سرور پروداکشن،
    پروکسی معکوس Nginx (مانند دامنه attarkhone.ip3.ir) و دامنه‌های سفارشی.
    این کلاس مانع از بروز خطای ۴۰۳ فوربیدن در درخواست‌های POST فرم‌ها و ایجکس سبد خرید می‌شود.
    """
    def _origin_verified(self, request):
        if super()._origin_verified(request):
            return True
        origin = request.META.get('HTTP_ORIGIN')
        if not origin:
            return False
        try:
            parsed = urllib.parse.urlsplit(origin)
            good_host = request.get_host().split(':')[0]
            origin_host = parsed.netloc.split(':')[0]
            if origin_host == good_host:
                return True
            if '*' in settings.ALLOWED_HOSTS or any(is_same_domain(origin_host, h.lstrip('.')) for h in settings.ALLOWED_HOSTS):
                return True
        except Exception:
            return False
        return False

    def _check_referer(self, request):
        try:
            return super()._check_referer(request)
        except Exception:
            referer = request.META.get('HTTP_REFERER')
            if not referer:
                raise
            try:
                parsed = urllib.parse.urlsplit(referer)
                good_host = request.get_host().split(':')[0]
                referer_host = parsed.netloc.split(':')[0]
                if referer_host == good_host:
                    return
                if '*' in settings.ALLOWED_HOSTS or any(is_same_domain(referer_host, h.lstrip('.')) for h in settings.ALLOWED_HOSTS):
                    return
            except Exception:
                pass
            raise


class DynamicCsrfTrustedOriginsMiddleware:
    """
    میدلور کمکی برای سازگاری گذشته‌نگر
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)


class MaintenanceModeMiddleware:
    """
    کارگاه ۳ کتاب: غیرفعال کردن موقت فروشگاه با امکان استثنا برای IPهای کارمندان
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        # همیشه دسترسی به ادمین، سلامت سیستم، استاتیک و رسانه مجاز است
        if path.startswith('/attar-management/') or path.startswith('/admin/') or path.startswith('/static/') or path.startswith('/media/') or path == '/health/':
            return self.get_response(request)

        try:
            setting = StoreSetting.get_settings()
        except Exception:
            return self.get_response(request)

        if setting.is_maintenance_mode:
            # بررسی احراز هویت کارمند یا سوپریوزر (کارگاه ۱ و ۳: عبور کارمندان مجاز)
            if request.user.is_authenticated and (request.user.is_staff or getattr(request.user, 'is_store_staff', False)):
                return self.get_response(request)

            # بررسی آی‌پی‌های سفید تعیین‌شده در پنل مدیریت
            client_ip = self.get_client_ip(request)
            allowed_ips = [ip.strip() for ip in setting.maintenance_allowed_ips.split(',') if ip.strip()]

            if client_ip in allowed_ips:
                return self.get_response(request)

            # نمایش صفحه رسمی در دست تعمیر (کارگاه ۳ کتاب)
            return render(
                request,
                'core/maintenance.html',
                {
                    'store_setting': setting,
                    'client_ip': client_ip,
                },
                status=503
            )

        return self.get_response(request)

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
