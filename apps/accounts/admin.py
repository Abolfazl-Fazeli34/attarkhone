from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'role', 'phone', 'is_active', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'phone', 'email')
    
    fieldsets = UserAdmin.fieldsets + (
        ('اطلاعات تکمیلی و نمایه کارمند (کارگاه ۱ و ۲)', {
            'fields': ('role', 'phone', 'address', 'postal_code', 'national_id')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('اطلاعات تکمیلی و نمایه کارمند (کارگاه ۱ و ۲)', {
            'fields': ('role', 'phone', 'address', 'postal_code', 'national_id')
        }),
    )
