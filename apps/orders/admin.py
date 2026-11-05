from django.contrib import admin
from .models import Order, OrderItem, BankReceipt, Cart, CartItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'variant_label', 'price', 'quantity')


class BankReceiptInline(admin.StackedInline):
    model = BankReceipt
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('tracking_code', 'full_name', 'phone', 'carrier', 'total_amount', 'status', 'is_paid', 'is_gift_wrapped', 'created_at')
    list_filter = ('status', 'is_paid', 'payment_method', 'is_gift_wrapped', 'carrier', 'created_at')
    search_fields = ('tracking_code', 'full_name', 'phone', 'city')
    inlines = [OrderItemInline, BankReceiptInline]
    
    fieldsets = (
        ('اطلاعات سفارش و تحویل‌گیرنده', {
            'fields': ('tracking_code', 'user', 'full_name', 'phone', 'email', 'province', 'city', 'address', 'postal_code', 'order_notes')
        }),
        ('ارسال، حمل و کادوپیچی (کارگاه ۱۰ و ۲۴)', {
            'fields': ('carrier', 'shipping_cost', 'is_gift_wrapped', 'gift_message', 'gift_cost')
        }),
        ('مالی و تخفیف‌ها (کارگاه ۱۷ و ۲۳)', {
            'fields': ('coupon', 'discount_amount', 'subtotal', 'total_amount', 'payment_method', 'is_paid')
        }),
        ('وضعیت و پردازش سفارش (کارگاه ۲۴)', {
            'fields': ('status', 'admin_notes')
        }),
    )


@admin.register(BankReceipt)
class BankReceiptAdmin(admin.ModelAdmin):
    list_display = ('order', 'bank_name', 'tracking_number', 'deposited_amount', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'bank_name')
    search_fields = ('tracking_number', 'order__tracking_code')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'created_at')
