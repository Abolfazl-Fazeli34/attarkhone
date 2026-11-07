from django.shortcuts import render, get_object_or_404
from django.views import View
from django.db.models import F
from .models import StaticPage, Article


class ArticleListView(View):
    """
    فهرست مقالات، آموزش‌ها و وبلاگ تندرستی
    کارگاه ۶ و ۲۷ (تولید محتوا و بهینه‌سازی سئو برای جذب ترافیک ارگانیک)
    """
    def get(self, request):
        articles = Article.objects.filter(is_published=True).order_by('-created_at')
        category = request.GET.get('category')
        if category:
            articles = articles.filter(category=category)
        
        categories = Article.objects.filter(is_published=True).values_list('category', flat=True).distinct()
        return render(request, 'pages/article_list.html', {
            'articles': articles,
            'categories': categories,
            'selected_category': category,
        })


class ArticleDetailView(View):
    """
    صفحه تکی مقاله آموزشی همراه با شمارنده بازدید و مقالات مرتبط
    """
    def get(self, request, slug):
        article = get_object_or_404(Article, slug=slug, is_published=True)
        # افزایش بازدید
        Article.objects.filter(id=article.id).update(views_count=F('views_count') + 1)
        article.refresh_from_db()
        
        related_articles = Article.objects.filter(is_published=True).exclude(id=article.id)[:3]
        return render(request, 'pages/article_detail.html', {
            'article': article,
            'related_articles': related_articles,
        })


class PageDetailView(View):
    """
    کارگاه ۶: نمایش محتوای صفحات ایستا
    مانند درباره ما، شرایط و ضوابط، روش ارسال و بسته‌بندی سبز، ضمانت مرجوعی
    """
    def get(self, request, slug):
        page = get_object_or_404(StaticPage, slug=slug, is_published=True)
        return render(request, 'pages/page_detail.html', {'page': page})


class ContactUsView(View):
    def get(self, request):
        return render(request, 'pages/contact_us.html')
