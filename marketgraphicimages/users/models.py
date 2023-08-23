from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import (MaxValueValidator, MinLengthValidator,
                                    MinValueValidator)
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from core.validators import date_is_past


class CustomUserManager(UserManager):
    def create_superuser(
        self, username: str, email: str, password: str, **extra_fields
    ):
        """
        Creates a superuser with the given username, email, password,
        and any additional fields.

        Args:
            username (str): The username for the superuser.
            email (str): The email address for the superuser.
            password (str): The password for the superuser.
            **extra_fields: Additional fields for the superuser.

        Returns:
            User: The created superuser.
        """

        user = self._create_user(username, email, password, **extra_fields)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()

        return user


class User(AbstractUser):

    username = models.CharField(
        max_length=30,
        verbose_name=_('Username'),
        unique=True,
        help_text=_(
            'Enter the username. Maximum of 30 characters.'
            'Use only English letters, numbers and symbols @/./+/-/_'
        ),
        validators=[ASCIIUsernameValidator(),
                    MinLengthValidator(limit_value=3)],
        error_messages={
            'unique': _('User with such a username already exists'),
        },
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='Email',
        unique=True,
        validators=[ASCIIUsernameValidator()],
        help_text=_('Enter the email.'),
        error_messages={
            'unique': _('User with such an email already exists'),
        },
    )
    first_name = models.CharField(
        max_length=53,
        blank=True,
        validators=[ASCIIUsernameValidator(),
                    MinLengthValidator(limit_value=1)],
        verbose_name=_('Name'),
        help_text=_('Enter your name'),
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        validators=[ASCIIUsernameValidator(),
                    MinLengthValidator(limit_value=1)],
        verbose_name=_('Surname'),
        help_text=_('Enter your surname'),
    )
    birthdate = models.DateField(
        null=True,
        verbose_name=_('Date of birth'),
        validators=[date_is_past],
        help_text=_('Enter your date of birth'),
    )
    is_active = models.BooleanField(
        verbose_name=_('Active'),
        default=False,
    )
    phone_number = PhoneNumberField(
        blank=True,
        verbose_name=_('Number phone'),
        help_text=_('Enter your Number phone'),
    )
    author = models.BooleanField(
        verbose_name=_('Author'),
        default=False,
    )
    confirmation_code = models.IntegerField(
        verbose_name=_('Confirmation code'),
        null=True,
        validators=[MinValueValidator(100000), MaxValueValidator(999999)],
    )

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ('email',)

    def __str__(self):
        return self.username[:15]

    @property
    def is_author(self):
        return self.author


class UserConnection(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Выберите из списка пользователя',
    )

    class Meta:
        abstract = True


class Subscription(UserConnection):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Автор',
        help_text='Выберите автора из списка',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                name='unique_subscription',
                fields=('user', 'author'),
            ),
        ]


class UserConfirmationCode(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='code_owner',
    )
    confirmation_code = models.CharField(
        max_length=6,
    )
    is_confirmed = models.BooleanField(
        default=False,
    )
