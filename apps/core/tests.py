from django.test import TestCase, Client
from django.urls import reverse
from core.models import StoreSetting
from accounts.models import User


class CoreWorkshopsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.setting = StoreSetting.get_settings()

    def test_maintenance_mode_middleware(self):
        """کارگاه ۳: تست حالت تعمیرات و دسترسی IP"""
        # حالت عادی: صفحه اصلی در دسترس است
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

        # فعال کردن حالت تعمیرات با آی‌پی غیرمجاز
        self.setting.is_maintenance_mode = True
        self.setting.maintenance_allowed_ips = "192.168.1.50"
        self.setting.save()

        # درخواست با IP دیگر (مثلا 10.0.0.1) باید 503 بدهد
        response = self.client.get(reverse('core:home'), REMOTE_ADDR='10.0.0.1')
        self.assertEqual(response.status_code, 503)
        self.assertContains(response, "فروشگاه عطارخونه موقتاً در دست تعمیر", status_code=503)

        # درخواست با IP مجاز باید 200 بدهد
        response = self.client.get(reverse('core:home'), REMOTE_ADDR='192.168.1.50')
        self.assertEqual(response.status_code, 200)

    def test_health_check_view(self):
        """کارگاه ۲۲: تست صفحه آزمایش صحت و سلامت ارتقا"""
        response = self.client.get(reverse('core:health_check'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "آزمایش صحت ارتقا و سلامت سامانه")
        self.assertContains(response, "اتصال پایگاه داده")
