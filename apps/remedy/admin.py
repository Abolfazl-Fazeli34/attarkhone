from django.contrib import admin
from .models import SymptomCategory, ChemicalDrug, DrugInteraction, HealthRemedyPackage, ConsultationBooking, PrescriptionOrder


@admin.register(SymptomCategory)
class SymptomCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'icon')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ChemicalDrug)
class ChemicalDrugAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'category')


@admin.register(DrugInteraction)
class DrugInteractionAdmin(admin.ModelAdmin):
    list_display = ('drug', 'product', 'severity')
    list_filter = ('severity', 'drug')
    search_fields = ('drug__name', 'product__name', 'warning_text')


@admin.register(HealthRemedyPackage)
class HealthRemedyPackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'discounted_package_price')
    filter_horizontal = ('products',)


@admin.register(ConsultationBooking)
class ConsultationBookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'symptom_category', 'preferred_time', 'status', 'created_at')
    list_filter = ('status', 'symptom_category')
    search_fields = ('name', 'phone', 'notes')


@admin.register(PrescriptionOrder)
class PrescriptionOrderAdmin(admin.ModelAdmin):
    list_display = ('tracking_code', 'patient_name', 'phone', 'doctor_name', 'status', 'estimated_cost', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('tracking_code', 'patient_name', 'phone', 'doctor_name', 'notes')
    readonly_fields = ('tracking_code', 'created_at')
