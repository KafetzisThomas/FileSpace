from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "is_active", "is_superuser", "enable_2fa", "date_joined", "last_login")
    list_filter = ("is_active", "is_superuser", "enable_2fa")
    fieldsets = UserAdmin.fieldsets + (("2FA Security", {"fields": ("enable_2fa", "otp_secret")}),)
    search_fields = ("username",)
    ordering = ("username",)
