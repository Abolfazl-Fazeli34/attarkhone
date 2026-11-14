from django.test import TestCase, Client
from django.urls import reverse
from remedy.models import ChemicalDrug, DrugInteraction, SymptomCategory, ConsultationBooking
from catalog.models import Product, Category


class RemedyDrugInteractionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="گیاهان دارویی", slug="herbs-remedy")
        self.product = Product.objects.create(
            name="گل گاوزبان",
            slug="gol-gavzaban-remedy",
            category=self.category,
            base_price=60000,
        )
        self.drug = ChemicalDrug.objects.create(
            name="وارفارین",
            category="رقیق‌کننده خون",
        )
        self.interaction = DrugInteraction.objects.create(
            drug=self.drug,
            product=self.product,
            severity="danger",
            warning_text="مصرف همزمان خطر خونریزی حاد دارد."
        )

    def test_drug_check_api(self):
        url = reverse('remedy:check_drug') + f'?drug_id={self.drug.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['drug_name'], 'وارفارین')
        self.assertEqual(data['interactions_count'], 1)
        self.assertEqual(data['interactions'][0]['severity'], 'danger')
        self.assertIn("خطر خونریزی", data['interactions'][0]['warning_text'])

    def test_consultation_booking_submission(self):
        url = reverse('remedy:consultation')
        # دریافت فرم
        res_get = self.client.get(url)
        self.assertEqual(res_get.status_code, 200)

        # ارسال فرم رزرو نوبت
        res_post = self.client.post(url, {
            'name': 'علی محمدی',
            'phone': '09129876543',
            'symptom_category': 'استرس و اضطراب',
            'preferred_time': 'صبح (۹ الی ۱۳)',
            'notes': 'نیاز به مشاوره دمنوش مناسب بی‌خوابی شبانه'
        })
        self.assertEqual(res_post.status_code, 302)

        booking = ConsultationBooking.objects.filter(phone='09129876543').first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.name, 'علی محمدی')
        self.assertEqual(booking.status, 'pending')

    def test_prescription_upload_and_track(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from remedy.models import PrescriptionOrder
        
        url_upload = reverse('remedy:prescription_upload')
        res_get = self.client.get(url_upload)
        self.assertEqual(res_get.status_code, 200)

        dummy_img = SimpleUploadedFile("prescription.jpg", b"fake_image_bytes", content_type="image/jpeg")
        res_post = self.client.post(url_upload, {
            'patient_name': 'زهرا قاسمی',
            'phone': '09351234567',
            'doctor_name': 'دکتر طب سنتی اصفهان',
            'patient_age': '۴۲ سال',
            'notes': 'داروهای کاهنده چربی خون و تقویت کبد',
            'prescription_image': dummy_img,
        })
        self.assertEqual(res_post.status_code, 200)
        prescription = PrescriptionOrder.objects.filter(phone='09351234567').first()
        self.assertIsNotNone(prescription)
        self.assertEqual(prescription.patient_name, 'زهرا قاسمی')
        self.assertEqual(prescription.status, 'pending')

        # استعلام آنلاین با کد رهگیری
        url_track = reverse('remedy:prescription_track') + f'?code={prescription.tracking_code}'
        res_track = self.client.get(url_track)
        self.assertEqual(res_track.status_code, 200)
        self.assertContains(res_track, prescription.tracking_code)
        self.assertContains(res_track, 'زهرا قاسمی')
