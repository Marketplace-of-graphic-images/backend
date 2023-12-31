from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

from marketgraphicimages.settings import ALLOWED_EXTENSIONS

from tags.models import Tag
from users.models import User, UserConnection


class Image(models.Model):
    """Model of images."""

    class LicenseType(models.TextChoices):
        """Class of choices licese types of images."""

        FREE = 'free', _('free')
        PAID = 'paid', _('paid')

    created = models.DateTimeField(
        verbose_name=_('Date of creation'),
        auto_now_add=True,
        help_text=_('Automatically sets the current date and time'),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Author'),
        help_text=_('Image author'),
    )
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=200,
        help_text=_('Enter the name'),
    )
    image = models.FileField(
        verbose_name=_('Image'),
        upload_to='images/',
        unique=True,
        help_text=_('Upload an image'),
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)
        ]
    )
    license = models.CharField(
        verbose_name=_('License'),
        max_length=15,
        choices=LicenseType.choices,
        help_text=_('Select license type')
    )
    price = models.IntegerField(
        verbose_name=_('Image price'),
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(999999)],
        help_text=_('Specify a price')
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagImage',
        verbose_name=_('Tag'),
        help_text=_('Select tags'),
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    def __str__(self):
        return str(
            (_('Author') + f': {str(self.author)} ' +
             _('Image name') + f': {self.name[:15]}')
        )


class ImageConnection(models.Model):
    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        verbose_name=_('Image'),
        help_text=_('Select image'),
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
        verbose_name = _('Favorite image')
        verbose_name_plural = _('Favorite images')
        ordering = ('image',)

    def __str__(self) -> str:
        return (f'{self.user.get_username} добавил в избранное '
                f'{self.image.name}')


class ShoppingCartImage(ImageConnection, UserConnection):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_shopping_cart',
                fields=('image', 'user'),
            ),
        ]
        verbose_name = _('Shopping cart image')
        verbose_name_plural = _('Shopping cart images')
        ordering = ('image',)


class TagImage(ImageConnection):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.DO_NOTHING,
        verbose_name=_('Tag'),
        help_text=_('Select tag'),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_image_tag',
                fields=['image', 'tag'],
            ),
        ]
        verbose_name = _('Tag image')
        verbose_name_plural = _('Tags image')


class DownloadImage(ImageConnection, UserConnection):
    class Meta:
        verbose_name = _('My download image')
        verbose_name_plural = _('My download images')
        ordering = ('user',)
