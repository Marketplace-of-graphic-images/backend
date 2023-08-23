from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Subscription, UserConfirmationCode

User = get_user_model()


@admin.register(User)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "phone_number",
    )
    search_fields = (
        "username",
        "email",
    )
    list_filter = (
        "username",
        "email",
    )
    empty_value_display = "---пусто---"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
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
