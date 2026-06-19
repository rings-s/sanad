from django.contrib import admin

from base.admin import PublishableAdminMixin
from .models import Content


@admin.register(Content)
class ContentAdmin(PublishableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'type', 'author', 'category', 'is_published', 'publish_at', 'created_at')
    list_filter = ('type', 'is_published', 'is_archived', 'category', 'subcategory')
    list_editable = ('is_published',)
    search_fields = ('title', 'body', 'original_text', 'translated_text', 'source_attribution')
    autocomplete_fields = ('category', 'subcategory')
    filter_horizontal = ('tags',)
    readonly_fields = ('public_id', 'slug', 'search_text', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Content', {
            'fields': ('type', 'title', 'body', 'featured_image'),
        }),
        ('Media', {
            'fields': ('youtube_url', 'audio_file', 'duration_seconds', 'document'),
            'description': 'Fill only the field relevant to this content type. Document accepts PDF or Word (.pdf, .doc, .docx) only.',
        }),
        ('Religious Reference', {
            'fields': ('original_text', 'translated_text', 'source_attribution'),
            'classes': ('collapse',),
        }),
        ('Classification', {
            'fields': ('category', 'subcategory', 'tags'),
        }),
        ('Publishing', {
            'fields': ('author', 'is_published', 'publish_at', 'is_archived'),
        }),
        ('System', {
            'fields': ('public_id', 'slug', 'search_text', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
