from django.contrib.sitemaps import Sitemap
from catalog.models import Product, Category
from pages.models import StaticPage


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.created_at


class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Category.objects.all()


class PageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return StaticPage.objects.filter(is_published=True).order_by('id')

    def lastmod(self, obj):
        return obj.updated_at
