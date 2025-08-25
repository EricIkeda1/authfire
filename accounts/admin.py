from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'firebase_uid', 'email_verified', 'is_staff', 'date_joined')
    list_filter = ('email_verified', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username', 'firebase_uid')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações pessoais', {'fields': ('first_name', 'last_name', 'email')}),
        ('Firebase', {'fields': ('firebase_uid', 'email_verified')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas importantes', {'fields': ('last_login', 'date_joined')}),
    )