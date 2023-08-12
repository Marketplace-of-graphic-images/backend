from core.validators import date_is_past
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


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

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ('email',)

    def __str__(self):
        return self.username[:15]
