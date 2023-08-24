from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import UserConfirmationCode

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
    )
    search_fields = (
        "username",
        'email',
    )
    list_filter = (
        'username',
        'email',
    )


@admin.register(UserConfirmationCode)
class UserConfirmationCodeAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'confirmation_code',
        'is_confirmed',
    )
    search_fields = (
        'user',
    )
    list_filter = (
        'user',
    )
    readonly_fields = (
        'user',
        'confirmation_code',
        'is_confirmed',
    )
    empty_value_display = '---пусто---'
