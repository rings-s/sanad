from django.contrib import admin

from .models import Category, Subcategory, Tag, SavedItem, Comment, ContentProgress, DailyGuidance


class PublishableAdminMixin:
    actions = ('make_published', 'make_unpublished', 'make_archived')

    @admin.action(description='Publish selected')
    def make_published(self, request, queryset):
        queryset.update(is_published=True)

    @admin.action(description='Unpublish selected')
    def make_unpublished(self, request, queryset):
        queryset.update(is_published=False)

    @admin.action(description='Archive selected')
    def make_archived(self, request, queryset):
        queryset.update(is_archived=True)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    search_fields = ('name',)
    readonly_fields = ('slug', 'created_at')


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug')
    list_filter = ('category',)
    search_fields = ('name',)
    autocomplete_fields = ('category',)
    readonly_fields = ('slug', 'created_at')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    readonly_fields = ('slug', 'created_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'status', 'created_at')
    list_filter = ('status',)
    list_editable = ('status',)
    search_fields = ('text', 'user__email')
    readonly_fields = ('public_id', 'created_at', 'updated_at')
    actions = ('approve_comments', 'reject_comments')

    @admin.action(description='Approve selected')
    def approve_comments(self, request, queryset):
        queryset.update(status=Comment.STATUS_APPROVED)

    @admin.action(description='Reject selected')
    def reject_comments(self, request, queryset):
        queryset.update(status=Comment.STATUS_REJECTED)


@admin.register(SavedItem)
class SavedItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'created_at')
    readonly_fields = ('public_id', 'created_at', 'updated_at')


@admin.register(ContentProgress)
class ContentProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'created_at')
    readonly_fields = ('public_id', 'created_at', 'updated_at')


@admin.register(DailyGuidance)
class DailyGuidanceAdmin(admin.ModelAdmin):
    list_display = ('date',)
    filter_horizontal = ('items',)
    readonly_fields = ('public_id', 'created_at', 'updated_at')
