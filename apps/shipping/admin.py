from django.contrib import admin
from .models import Province, Carrier


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'delivery_time', 'free_shipping_min_order', 'is_eco_friendly', 'is_active')
    list_filter = ('is_active', 'is_eco_friendly')
