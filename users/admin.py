from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django import forms

from .models import Profile
User = get_user_model()


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = '__all__'

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    add_form = UserCreationForm

    list_display = ('id', 'first_name', 'last_name', 'email', 'password', 'phone_number', 'avatar', 'is_active', 'is_staff')
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
            'fields': ('email', 'password', 'first_name', 'last_name', 'phone_number', 'avatar', 'avatar_coord',
                       'is_active', 'is_staff'),
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
