from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils.translation import gettext_lazy as _

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'firebase_uid', 'email_verified', 'is_staff', 'created_at')
    list_filter = ('email_verified', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('email', 'username', 'firebase_uid')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Informações pessoais'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Firebase'), {'fields': ('firebase_uid', 'email_verified')}),
        (_('Datas importantes'), {'fields': ('created_at', 'updated_at')}),
        (_('Permissões'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Datas de login'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )