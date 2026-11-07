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
