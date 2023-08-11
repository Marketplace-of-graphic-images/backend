from django.core.validators import MinLengthValidator
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.db import models

from marketgraphicimages.core.validators import date_is_past


class User(AbstractUser):

    username = models.CharField(
        max_length=30,
        verbose_name='юзернейм пользователя',
        unique=True,
        help_text=(
            'Введите юзернейм пользователя. Максимум 30 символов. '
            'Используйте только английские буквы, цифры и символы @/./+/-/_'
        ),
        validators=[ASCIIUsernameValidator(),
                    MinLengthValidator(limit_value=3)],
        error_messages={
            'unique': 'Пользователь с таким юзернеймом уже существует',
        },
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='email',
        unique=True,
        validators=[ASCIIUsernameValidator()],
        help_text='Введите адрес электронной почты',
        error_messages={
            'unique': 'Пользователь с такой почтой уже существует',
        },
    )
    first_name = models.CharField(
        max_length=53,
        blank=True,
        validators=[ASCIIUsernameValidator(),
                    MinLengthValidator(limit_value=1)],
        verbose_name='имя',
        help_text='Введите ваше имя',
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        validators=[ASCIIUsernameValidator(),
                    MinLengthValidator(limit_value=1)],
        verbose_name='фамилия',
        help_text='Введите вашу фамилию',
    )
    birthdate = models.DateField(
        blank=True,
        verbose_name='дата рождения',
        validators=[date_is_past()],
        help_text='Введите вашу дату рождения',
    )
    is_active = models.BooleanField(
        verbose_name="Активирован",
        default=False,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)

    def __str__(self):
        return self.username[:15]
