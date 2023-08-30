from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from tags.models import Tag

from users.models import User, UserConnection

price_type = [('Платно', 'Платно'), ('Бесплатно', 'Бесплатно'), ]


class Image(models.Model):
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        help_text='Автоматически устанавливается текущая дата и время',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Автор',
        help_text='Автор изображения',
    )
    name = models.CharField(
        'Название',
        unique=True,
        max_length=200,
        help_text='Введите название',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='Images/',
        unique=True,
        help_text='Добавьте изображение',
    )
    license = models.CharField(
        max_length=15,
        choices=price_type,
    )
    price = models.IntegerField(
        verbose_name='Цена изображения',
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(999999)],
    )
    format = models.CharField(
        max_length=5,
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagImage',
        verbose_name='Теги',
        help_text='Выберите теги',
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'

    def __str__(self):
        return (
            f'Автор: {str(self.author)} Название: {self.name[:15]}'
        )


class ImageConnection(models.Model):
    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        verbose_name='Изображение',
        help_text='Выберите изображения',
    )

    class Meta:
        abstract = True


class FavoriteImage(ImageConnection, UserConnection):

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_favorite',
                fields=('image', 'user'),
            ),
        ]
        verbose_name = 'Любимое изображение'
        verbose_name_plural = 'Любимые изображения'


class ShoppingCartImage(ImageConnection, UserConnection):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_shopping_cart',
                fields=('image', 'user'),
            ),
        ]
        verbose_name = 'Купленное изображение'
        verbose_name_plural = 'Купленные изображения'


class TagImage(ImageConnection):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.DO_NOTHING,
        verbose_name='Тег',
        help_text='Выберите из списка тег',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_image_tag',
                fields=['image', 'tag'],
            ),
        ]
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
