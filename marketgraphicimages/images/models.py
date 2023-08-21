# from django.db import models

# from users.models import User, UserConnection


# class Image(models.Model):
#     created = models.DateTimeField(
#         'Дата создания',
#         auto_now_add=True,
#         help_text='Автоматически устанавливается текущая дата и время',
#     )
#     author = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='images',
#         verbose_name='Автор',
#         help_text='Автор изображения',
#     )
#     name = models.CharField(
#         'Название',
#         unique=True,
#         max_length=200,
#         help_text='Введите название',
#     )
#     image = models.ImageField(
#         'Картинка',
#         upload_to='Images/',
#         unique=True,
#         help_text='Добавьте изображение',
#     )

#     class Meta:
#         ordering = ('-created',)
#         verbose_name = 'Изображение'
#         verbose_name_plural = 'Изображения'

#     def __str__(self):
#         return (
#             f'Автор: {str(self.author)} Название: {self.name[:15]}'
#         )


# class ImageConnection(models.Model):
#     image = models.ForeignKey(
#         Image,
#         on_delete=models.CASCADE,
#         verbose_name='Изображение',
#         help_text='Выберите изображения',
#     )

#     class Meta:
#         abstract = True


# class FavoriteImage(ImageConnection, UserConnection):

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 name='unique_favorite',
#                 fields=('image', 'user'),
#             ),
#         ]
#         verbose_name = 'Любимое изображение'
#         verbose_name_plural = 'Любимые изображения'


# class ShoppingCartImage(ImageConnection, UserConnection):
#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 name='unique_shopping_cart',
#                 fields=('image', 'user'),
#             ),
#         ]
#         verbose_name = 'Купленное изображение'
#         verbose_name_plural = 'Купленные изображения'
