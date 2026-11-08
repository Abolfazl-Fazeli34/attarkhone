from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()


class EmailAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='sara_rad',
            email='sara@example.com',
            password='Password123!',
            first_name='سارا',
            last_name='راد',
            phone='09120000001'
        )

    def test_login_with_username(self):
        """ورود موفق با نام کاربری"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'sara_rad',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_with_email(self):
        """ورود موفق با نشانی ایمیل"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'sara@example.com',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_with_email_case_insensitive(self):
        """ورود بدون حساسیت به حروف بزرگ و کوچک ایمیل"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'SARA@EXAMPLE.COM',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_register_new_user_with_email(self):
        """ثبت‌نام کاربر جدید با ایمیل معتبر و ارسال ایمیل خوش‌آمدگویی"""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'new_customer',
            'email': 'newcustomer@example.com',
            'first_name': 'رضا',
            'last_name': 'کمالی',
            'phone': '09121111111',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='newcustomer@example.com').exists())

    def test_password_reset_flow(self):
        """درخواست بازیابی گذرواژه و ارسال ایمیل حاوی توکن معتبر"""
        response = self.client.post(reverse('accounts:password_reset'), {
            'email': 'sara@example.com'
        })
        self.assertEqual(response.status_code, 302)

        # شبیه‌سازی تایید توکن
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        confirm_url = reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        confirm_resp = self.client.post(confirm_url, {
            'password': 'NewPassword123!',
            'password_confirm': 'NewPassword123!'
        })
        self.assertEqual(confirm_resp.status_code, 302)

        # بررسی ورود با گذرواژه جدید
        login_resp = self.client.post(reverse('accounts:login'), {
            'username': 'sara@example.com',
            'password': 'NewPassword123!'
        })
        self.assertEqual(login_resp.status_code, 302)
