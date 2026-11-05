from django.contrib import admin
from .models import StoreSetting


@admin.register(StoreSetting)
class StoreSettingAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'phone', 'email', 'is_maintenance_mode')
    
    fieldsets = (
        ('اطلاعات عمومی فروشگاه (کارگاه ۴)', {
            'fields': ('store_name', 'slogan', 'phone', 'mobile', 'email', 'province', 'city', 'address', 'postal_code', 'about_summary')
        }),
        ('لوگو و فاوآیکون (کارگاه ۵)', {
            'fields': ('logo', 'favicon')
        }),
        ('حالت تعمیرات و امنیت دسترسی (کارگاه ۳)', {
            'fields': ('is_maintenance_mode', 'maintenance_message', 'maintenance_allowed_ips'),
            'description': 'کارگاه ۳: با فعال‌سازی حالت تعمیرات، تنها کارمندان و IPهای تعیین‌شده به سایت دسترسی خواهند داشت.'
        }),
        ('هزینه‌های پایه و کادوپیچی (کارگاه ۲۴)', {
            'fields': ('gift_wrap_cost', 'free_shipping_threshold')
        }),
        ('شبکه‌های اجتماعی (کارگاه ۲۵ و بازارگردانی)', {
            'fields': ('instagram', 'telegram', 'eitaa', 'bale')
        }),
    )

    def has_add_permission(self, request):
        # فقط یک رکورد تنظیمات مجاز است (Singleton)
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
