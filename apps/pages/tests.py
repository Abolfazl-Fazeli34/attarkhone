from django.test import TestCase, Client
from django.urls import reverse
from pages.models import Article, StaticPage


class ArticleTestCase(TestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="خواص درمانی گل گاوزبان و کاهش استرس",
            slug="borage-health-benefits-test",
            summary="گل گاوزبان یکی از معتبرترین آرام‌بخش‌های طبیعی است.",
            content="متن کامل خواص گل گاوزبان و نحوه دم‌آوری صحیح آن.",
            category="دمنوش‌های آرام‌بخش",
            reading_time=4,
            views_count=10,
        )

    def test_article_list_view(self):
        client = Client()
        response = client.get(reverse('pages:article_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "خواص درمانی گل گاوزبان")

    def test_article_detail_increments_views(self):
        client = Client()
        initial_views = self.article.views_count
        response = client.get(reverse('pages:article_detail', kwargs={'slug': self.article.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "خواص درمانی گل گاوزبان")
        
        self.article.refresh_from_db()
        self.assertEqual(self.article.views_count, initial_views + 1)
