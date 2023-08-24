from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import (FavoriteImage, Image,
                     ShoppingCartImage, TagImage)

User = get_user_model()


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'author',
        'created',
        'license',
        'tip',
        'price',
    )
    search_fields = (
        'author',
        'name',
    )
    list_filter = (
        'name',
        'author',
        'tags',
    )


@admin.register(FavoriteImage)
class FavoriteImageAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'image',
        'user',
    )
    list_filter = (
        'image',
        'user',
    )


@admin.register(ShoppingCartImage)
class ShoppingCartRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'image',
        'user',
    )
    list_filter = (
        'image',
        'user',
    )


@admin.register(TagImage)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'image',
        'tag',
    )
    list_filter = (
        'image',
        'tag',
    )
