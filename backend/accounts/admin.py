from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    readonly_fields = ('google_uid',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('email', 'username', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active')
    list_editable = ('role',)
    search_fields = ('email', 'username')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Sanad Role', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Sanad Role', {'fields': ('email', 'role')}),
    )
