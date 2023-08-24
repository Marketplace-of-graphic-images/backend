from django.db import models


class Tag(models.Model):
    name = models.CharField(
        'Название',
        unique=True,
        max_length=200,
        help_text='Введите название',
    )
    slug = models.SlugField(
        'Slug',
        null=False,
        help_text='Введите Slug',
        unique=True,
    )

    class Meta:
        ordering = ('-name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'Название: {self.name[:15]} Адрес: {str(self.slug)}'
