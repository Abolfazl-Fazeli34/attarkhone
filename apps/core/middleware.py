from django.shortcuts import render
from .models import StoreSetting


class MaintenanceModeMiddleware:
    """
    کارگاه ۳ کتاب: غیرفعال کردن موقت فروشگاه با امکان استثنا برای IPهای کارمندان
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        # همیشه دسترسی به ادمین و سلامت سیستم مجاز است
        if path.startswith('/attar-management/') or path.startswith('/admin/') or path.startswith('/static/'):
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
