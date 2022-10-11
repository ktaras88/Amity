from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group

from .models import User, Profile


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'avatar', 'is_active', 'is_staff')
    list_display_links = ('id', 'first_name', 'last_name', 'email')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email',)
    ordering = ('id', 'email',)
    filter_horizontal = ()
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('first_name', 'last_name', 'phone_number', 'avatar', 'avatar_coord')}),
        ('Permissions', {'fields': ('is_active', 'is_staff')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email',),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role')
    list_display_links = ('id', 'user', 'role')
    list_filter = ['role']
    search_fields = ('role',)
    ordering = ('role',)
    fieldsets = (
        (None, {'fields': ('user', 'role')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user', 'role'),
        }),
    )


admin.site.unregister(Group)
