from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import ConfirmationCode, Subscription, UserConfirmationCode

User = get_user_model()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'author',
    )
    search_fields = (
        'user',
        'author',
    )
    list_filter = (
        'user',
        'author',
    )
    list_editable = (
        'user',
        'author'
    )


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'profile_photo'
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


@admin.register(ConfirmationCode)
class ConfirmationCodeAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'confirmation_code',
    )
    search_fields = (
        'email',
    )
    list_filter = (
        'email',
    )
    readonly_fields = (
        'email',
        'confirmation_code',
    )
    empty_value_display = '---пусто---'
