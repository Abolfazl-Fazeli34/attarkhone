from django.test import TestCase, Client
from django.urls import reverse
from remedy.models import ChemicalDrug, DrugInteraction, SymptomCategory
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
