from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from catalog.models import Product, Category, Wishlist

User = get_user_model()


class WishlistTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="دمنوش‌ها", slug="damnoosh")
        self.product = Product.objects.create(
            name="دمنوش آرامش‌بخش",
            slug="damnoosh-aramesh",
            category=self.category,
            base_price=99000,
        )
        self.user = User.objects.create_user(
            username="reza_health",
            password="Password123!",
            first_name="رضا"
        )

    def test_unauthenticated_wishlist_toggle_returns_401(self):
        client = Client()
        url = reverse('catalog:wishlist_toggle', kwargs={'product_id': self.product.id})
        response = client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertTrue(data['require_login'])

    def test_authenticated_wishlist_toggle_and_view(self):
        client = Client()
        client.login(username="reza_health", password="Password123!")

        url = reverse('catalog:wishlist_toggle', kwargs={'product_id': self.product.id})
        # افزودن به لیست
        res_add = client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res_add.status_code, 200)
        self.assertTrue(res_add.json()['is_added'])
        self.assertEqual(res_add.json()['wishlist_count'], 1)
        self.assertEqual(Wishlist.objects.filter(user=self.user, product=self.product).count(), 1)

        # مشاهده صفحه لیست علاقه‌مندی‌ها
        res_view = client.get(reverse('catalog:wishlist'))
        self.assertEqual(res_view.status_code, 200)
        self.assertContains(res_view, "دمنوش آرامش‌بخش")

        # حذف از لیست
        res_remove = client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res_remove.status_code, 200)
        self.assertFalse(res_remove.json()['is_added'])
        self.assertEqual(res_remove.json()['wishlist_count'], 0)
        self.assertEqual(Wishlist.objects.filter(user=self.user, product=self.product).count(), 0)


class FacetedSearchTestCase(TestCase):
    """
    کارگاه ۱۸ کتاب: آزمون جستجوی لایه‌ای و فیلترهای چندگانه کاتالوگ
    """
    def setUp(self):
        self.client = Client()
        self.cat_tea = Category.objects.create(name="دمنوش‌ها", slug="damnoosh")
        self.cat_herb = Category.objects.create(name="گیاهان دارویی", slug="herbs")

        self.p1 = Product.objects.create(
            name="دمنوش بابونه آرام‌بخش",
            slug="damnoosh-baboneh",
            category=self.cat_tea,
            base_price=60000,
            temperament="warm",
            is_organic=True
        )
        self.p2 = Product.objects.create(
            name="عصاره کاسنی خنک",
            slug="aragh-kasni",
            category=self.cat_herb,
            base_price=120000,
            temperament="cold",
            is_organic=False
        )

    def test_filter_by_category(self):
        res = self.client.get(reverse('catalog:product_list') + '?cat=damnoosh')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "دمنوش بابونه")
        self.assertNotContains(res, "عصاره کاسنی خنک")

    def test_filter_by_temperament(self):
        res = self.client.get(reverse('catalog:product_list') + '?temperament=cold')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "عصاره کاسنی خنک")
        self.assertNotContains(res, "دمنوش بابونه")

    def test_filter_by_price_range(self):
        res = self.client.get(reverse('catalog:product_list') + '?min_price=100000&max_price=150000')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "عصاره کاسنی خنک")
        self.assertNotContains(res, "دمنوش بابونه")

    def test_product_detail_renders_coa_and_dosage(self):
        res = self.client.get(reverse('catalog:product_detail', kwargs={'slug': self.p1.slug}))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "شناسنامه ارزیابی فیتوشیمیایی")
        self.assertContains(res, "فارماکوپه")
        self.assertContains(res, "طبع و مزاج گیاه‌شناسی و مصلح اختصاصی")
        self.assertContains(res, "دوز درمانی مجاز")

    def test_category_get_display_image_fallback(self):
        self.assertIn(".jpg", self.cat_tea.get_display_image)
        self.assertIn(".jpg", self.cat_herb.get_display_image)

    def test_product_list_pagination_context(self):
        res = self.client.get(reverse('catalog:product_list'))
        self.assertEqual(res.status_code, 200)
        self.assertIn('page_obj', res.context)
        self.assertEqual(res.context['page_obj'].number, 1)

    def test_product_review_submission(self):
        from catalog.models import ProductReview
        url = reverse('catalog:add_review', kwargs={'product_id': self.p1.id})
        res = self.client.post(url, {
            'author_name': 'سحر کرمانی',
            'author_phone': '09120001122',
            'rating': '5',
            'comment': 'بسیار عطر و طعم مطبوعی داشت و آرامش‌بخش بود.'
        })
        self.assertEqual(res.status_code, 302)
        review = ProductReview.objects.filter(product=self.p1, author_name='سحر کرمانی').first()
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, 5)

