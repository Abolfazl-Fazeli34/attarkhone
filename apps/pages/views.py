from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import StaticPage


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
