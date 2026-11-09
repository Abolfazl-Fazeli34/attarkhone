from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.db.models import F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import StaticPage, Article, ContactMessage


class ArticleListView(View):
    """
    فهرست مقالات، آموزش‌ها و وبلاگ تندرستی
    کارگاه ۶ و ۲۷ (تولید محتوا و بهینه‌سازی سئو برای جذب ترافیک ارگانیک)
    """
    def get(self, request):
        articles_qs = Article.objects.filter(is_published=True).order_by('-created_at')
        category = request.GET.get('category')
        if category:
            articles_qs = articles_qs.filter(category=category)
        
        categories = Article.objects.filter(is_published=True).values_list('category', flat=True).distinct()
        
        paginator = Paginator(articles_qs, 6)
        page_number = request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            page_obj = paginator.page(1)

        return render(request, 'pages/article_list.html', {
            'articles': page_obj,
            'page_obj': page_obj,
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

    def post(self, request):
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not full_name or not phone or not message:
            messages.error(request, 'لطفاً نام، شماره تماس و متن پیام خود را وارد فرمایید.')
            return render(request, 'pages/contact_us.html', {
                'full_name': full_name,
                'phone': phone,
                'email': email,
                'subject': subject,
                'message': message,
            })

        ContactMessage.objects.create(
            full_name=full_name,
            phone=phone,
            email=email,
            subject=subject or 'پیام عمومی از فرم تماس با ما',
            message=message
        )
        messages.success(request, 'پیام و درخواست مشاوره شما با موفقیت دریافت گردید. کارشناسان پشتیبانی و داروسازان سنتی عطارخونه به زودی با شما تماس خواهند گرفت.')
        return redirect('pages:contact_us')
