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
        """ثبت‌نام کاربر جدید با ایمیل معتبر، صدور کد ۵ رقمی OTP و تایید موفق"""
        from accounts.models import EmailOTP

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
        self.assertIn(reverse('accounts:verify_email'), response.url)

        # بازیابی کد OTP ایجادشده
        otp = EmailOTP.objects.filter(email='newcustomer@example.com', purpose='register').first()
        self.assertIsNotNone(otp)
        self.assertEqual(len(otp.code), 5)

        # تایید با کد ۵ رقمی
        verify_resp = self.client.post(reverse('accounts:verify_email'), {
            'otp_code': otp.code
        })
        self.assertEqual(verify_resp.status_code, 302)
        self.assertTrue(User.objects.filter(email='newcustomer@example.com').exists())

    def test_login_with_otp_flow(self):
        """ورود بدون رمز عبور با کد یکبار مصرف ایمیل (OTP Login)"""
        from accounts.models import EmailOTP

        # مرحله اول: درخواست ارسال کد یکبار مصرف
        req_resp = self.client.post(reverse('accounts:login_otp'), {
            'step': 'send_otp',
            'email': 'sara@example.com'
        })
        self.assertEqual(req_resp.status_code, 200)

        otp = EmailOTP.objects.filter(email='sara@example.com', purpose='login').first()
        self.assertIsNotNone(otp)

        # مرحله دوم: ورود با کد دریافتی
        verify_resp = self.client.post(reverse('accounts:login_otp'), {
            'step': 'verify_otp',
            'email': 'sara@example.com',
            'otp_code': otp.code
        })
        self.assertEqual(verify_resp.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_seller_panel_and_qr_label(self):
        """تست پنل اختصاصی فروشنده، کاتالوگ و صدور بارکد QR"""
        from accounts.models import SellerProfile
        from catalog.models import Category, Product

        seller = User.objects.create_user(
            username='herb_farm',
            email='farm@example.com',
            password='Password123!',
            role='seller'
        )
        SellerProfile.objects.create(
            user=seller,
            store_name='مزرعه گل‌های کوهستان',
            shaba_number='IR112233445566778899001122',
            national_id_or_registration='1234567890'
        )
        cat = Category.objects.create(name='گیاهان دارویی خالص', slug='herbs-test')
        prod = Product.objects.create(
            seller=seller,
            name='اسطوخودوس فرانسوی',
            slug='french-lavender',
            category=cat,
            base_price=120000,
            stock=25
        )

        # ورود فروشنده
        self.client.force_login(seller)

        # پیشخوان فروشنده
        dash_res = self.client.get(reverse('accounts:seller_dashboard'))
        self.assertEqual(dash_res.status_code, 200)

        # کاتالوگ فروشنده
        prod_res = self.client.get(reverse('accounts:seller_products'))
        self.assertEqual(prod_res.status_code, 200)

        # صدور شناسنامه و بارکد QR
        qr_res = self.client.get(reverse('accounts:seller_product_qr', kwargs={'product_id': prod.id}))
        self.assertEqual(qr_res.status_code, 200)
        self.assertContains(qr_res, 'data:image/png;base64,')

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
