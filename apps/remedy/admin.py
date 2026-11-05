from django.contrib import admin
from .models import SymptomCategory, ChemicalDrug, DrugInteraction, HealthRemedyPackage


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
