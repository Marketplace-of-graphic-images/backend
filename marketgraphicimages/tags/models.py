from django.db import models
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    name = models.CharField(
        verbose_name=_('Name'),
        unique=True,
        max_length=200,
        help_text=_('Enter the name'),
    )
    slug = models.SlugField(
        verbose_name=_('Slug'),
        null=False,
        help_text=_('Enter the slug'),
        unique=True,
    )

    class Meta:
        ordering = ('-name',)
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def __str__(self):
        return f'Название: {self.name[:15]} Адрес: {str(self.slug)}'
