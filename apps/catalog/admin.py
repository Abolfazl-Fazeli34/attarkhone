from django.contrib import admin
from .models import Category, Brand, Supplier, Product, ProductVariant, ProductFeature, Wishlist, ProductReview


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    verbose_name = "مشخصه وزنی (کارگاه ۱۳)"
    verbose_name_plural = "مشخصه‌های کالا (Attributes - کارگاه ۱۳)"


class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 1
    verbose_name = "ویژگی فنی (کارگاه ۱۴)"
    verbose_name_plural = "ویژگی‌های ثابت کالا (Features - کارگاه ۱۴)"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'website')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone')
    search_fields = ('name', 'contact_person')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'temperament', 'base_price', 'discount_percent', 'stock', 'is_featured', 'is_organic')
    list_filter = ('category', 'temperament', 'is_organic', 'is_featured', 'brand')
    search_fields = ('name', 'short_description', 'meta_keywords')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline, ProductFeatureInline]
    
    fieldsets = (
        ('اطلاعات عمومی محصول', {
            'fields': ('name', 'slug', 'category', 'brand', 'supplier', 'image', 'is_featured')
        }),
        ('طبع و قیمت‌گذاری', {
            'fields': ('temperament', 'base_price', 'discount_percent', 'stock', 'is_organic', 'is_eco_packaging')
        }),
        ('توضیحات و خواص گیاه', {
            'fields': ('short_description', 'description')
        }),
        ('بهینه‌سازی برای موتور جستجو و گوگل (کارگاه ۲۶ و ۲۷)', {
            'fields': ('meta_title', 'meta_keywords', 'meta_description'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'product', 'rating', 'is_approved', 'created_at', 'replied_at')
    list_filter = ('is_approved', 'rating', 'created_at')
    search_fields = ('author_name', 'comment', 'reply', 'product__name')
    list_editable = ('is_approved',)
    readonly_fields = ('created_at',)
