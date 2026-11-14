from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.contrib import messages

from .models import SymptomCategory, ChemicalDrug, DrugInteraction, HealthRemedyPackage, ConsultationBooking, PrescriptionOrder
from catalog.models import Product
from orders.views import get_or_create_cart
from orders.models import CartItem
from core.emails import send_consultation_confirmation_email


class RemedyWizardView(View):
    """
    موتور تعاملی عارضه‌یاب تندرستی و تداخلات دارویی (نوآوری پودمان ۱ و ۲)
    """
    def get(self, request):
        categories = SymptomCategory.objects.all()
        drugs = ChemicalDrug.objects.all().order_by('name')
        
        category_id = request.GET.get('category')
        selected_category = None
        packages = []
        if category_id and category_id.isdigit():
            selected_category = get_object_or_404(SymptomCategory, id=int(category_id))
            packages = selected_category.packages.prefetch_related('products').all()

        context = {
            'categories': categories,
            'selected_category': selected_category,
            'packages': packages,
            'drugs': drugs,
        }
        return render(request, 'remedy/wizard.html', context)


class DrugCheckAPIView(View):
    """
    وب‌سرویس سریع بررسی تداخل داروی شیمیایی با گیاهان دارویی
    """
    def get(self, request):
        drug_id = request.GET.get('drug_id')
        if not drug_id or not drug_id.isdigit():
            return JsonResponse({'status': 'error', 'message': 'شناسه داروی شیمیایی نامعتبر است.'})

        drug = get_object_or_404(ChemicalDrug, id=int(drug_id))
        interactions = DrugInteraction.objects.filter(drug=drug).select_related('product')
        
        results = []
        for inter in interactions:
            results.append({
                'product_name': inter.product.name,
                'severity': inter.severity,
                'severity_display': inter.get_severity_display(),
                'warning_text': inter.warning_text,
            })

        return JsonResponse({
            'status': 'ok',
            'drug_name': drug.name,
            'drug_category': drug.category,
            'interactions_count': len(results),
            'interactions': results,
        })


class AddPackageToCartView(View):
    """
    افزودن مستقیم تمامی محصولات پکیج پیشنهادی به سبد خرید
    """
    def post(self, request, package_id):
        package = get_object_or_404(HealthRemedyPackage, id=package_id)
        cart = get_or_create_cart(request)

        added_names = []
        for product in package.products.all():
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                variant=None,
                defaults={'quantity': 1}
            )
            if not created:
                cart_item.quantity += 1
                cart_item.save()
            added_names.append(product.name)

        messages.success(
            request,
            f'پکیج سلامت «{package.title}» شامل ({", ".join(added_names)}) با موفقیت به سبد خرید افزوده شد.'
        )
        return redirect('orders:cart')


class ConsultationBookingView(View):
    """
    ثبت درخواست نوبت مشاوره تخصصی رایگان با متخصصان طب سنتی
    (پیوند دکمه طلایی هیرو بنر صفحه اصلی و فرم اختصاصی)
    """
    def get(self, request):
        categories = SymptomCategory.objects.all()
        initial_name = ''
        initial_phone = ''
        if request.user.is_authenticated:
            initial_name = request.user.get_full_name() or request.user.username
            initial_phone = getattr(request.user, 'phone', '')

        return render(request, 'remedy/consultation_form.html', {
            'categories': categories,
            'initial_name': initial_name,
            'initial_phone': initial_phone,
        })

    def post(self, request):
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        symptom_category = request.POST.get('symptom_category', 'مشاوره عمومی تندرستی')
        preferred_time = request.POST.get('preferred_time', 'صبح (۹ الی ۱۳)')
        notes = request.POST.get('notes', '').strip()

        if not name or not phone:
            messages.error(request, 'لطفاً نام و نام خانوادگی و شماره تماس معتبر خود را وارد فرمایید.')
            return redirect('remedy:consultation')

        booking = ConsultationBooking.objects.create(
            name=name,
            phone=phone,
            symptom_category=symptom_category,
            preferred_time=preferred_time,
            notes=notes,
            status='pending',
        )

        # ارسال اعلان ایمیل به مدیر و متخصصان عطارخونه
        send_consultation_confirmation_email(booking, request)

        messages.success(
            request,
            f'درخواست نوبت مشاوره شما با موفقیت ثبت گردید (کد پیگیری: #{booking.id}). متخصصان طب سنتی عطارخونه در بازه زمانی «{preferred_time}» با شما تماس خواهند گرفت.'
        )
        return redirect('remedy:consultation')


class PrescriptionUploadView(View):
    """
    سرویس ارسال و بارگذاری نسخه پزشک طب سنتی
    جهت بررسی تخصصی فیتوتراپیست و آماده‌سازی اقلام دارویی
    """
    def get(self, request):
        initial_name = ''
        initial_phone = ''
        if request.user.is_authenticated:
            initial_name = request.user.get_full_name() or request.user.username
            initial_phone = getattr(request.user, 'phone', '')

        return render(request, 'remedy/prescription_upload.html', {
            'initial_name': initial_name,
            'initial_phone': initial_phone,
        })

    def post(self, request):
        patient_name = request.POST.get('patient_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        doctor_name = request.POST.get('doctor_name', '').strip()
        patient_age = request.POST.get('patient_age', '').strip()
        notes = request.POST.get('notes', '').strip()
        prescription_image = request.FILES.get('prescription_image')

        if not patient_name or not phone or not prescription_image:
            messages.error(request, 'لطفاً نام، شماره تماس و تصویر واضح نسخه پزشک را بارگذاری فرمایید.')
            return redirect('remedy:prescription_upload')

        # تولید کد رهگیری منحصربه‌فرد نسخه
        tracking_code = PrescriptionOrder.generate_tracking_code()
        while PrescriptionOrder.objects.filter(tracking_code=tracking_code).exists():
            tracking_code = PrescriptionOrder.generate_tracking_code()

        prescription = PrescriptionOrder.objects.create(
            patient_name=patient_name,
            phone=phone,
            doctor_name=doctor_name,
            patient_age=patient_age,
            prescription_image=prescription_image,
            notes=notes,
            tracking_code=tracking_code,
            status='pending',
        )

        messages.success(
            request,
            f'نسخه شما با موفقیت دریافت گردید! کد رهگیری نسخه شما: {tracking_code} می‌باشد. کارشناسان داروسازی عطارخونه پس از بررسی اولیه با شما تماس خواهند گرفت.'
        )
        return render(request, 'remedy/prescription_success.html', {'prescription': prescription})


class PrescriptionTrackView(View):
    """
    استعلام وضعیت نسخه ارسالی با کد رهگیری
    """
    def get(self, request):
        code = request.GET.get('code', '').strip()
        prescription = None
        if code:
            prescription = PrescriptionOrder.objects.filter(tracking_code__iexact=code).first()
            if not prescription:
                messages.warning(request, 'نسخه‌ای با این شناسه رهگیری یافت نشد.')

        return render(request, 'remedy/prescription_track.html', {
            'prescription': prescription,
            'search_code': code,
        })
