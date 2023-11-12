from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import ConfirmationCode, Subscription, UserConfirmationCode

User = get_user_model()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'subscriber',
        'author',
    )
    search_fields = (
        'subscriber',
        'author',
    )
    list_filter = (
        'subscriber',
        'author',
    )
    list_editable = (
        'subscriber',
        'author',
    )


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'profile_photo',
        'role',
    )
    fieldsets = UserAdmin.fieldsets
    fieldsets[1][1]['fields'] = ('role', 'email',)
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
