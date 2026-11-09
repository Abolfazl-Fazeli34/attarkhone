from django.contrib import admin
from .models import StaticPage, Article, ContactMessage


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'updated_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'reading_time', 'views_count', 'is_published', 'created_at')
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'summary', 'content')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('full_name', 'phone', 'email', 'message', 'subject')
    list_editable = ('is_read',)
    readonly_fields = ('created_at',)
