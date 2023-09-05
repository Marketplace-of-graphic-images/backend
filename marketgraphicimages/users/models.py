from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import (
    MinLengthValidator,
)
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Model of users."""
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
        max_length=320,
        verbose_name='Email',
        unique=True,
        validators=[ASCIIUsernameValidator()],
        help_text=_('Enter the email.'),
        error_messages={
            'unique': _('User with such an email already exists'),
        },
    )
    author = models.BooleanField(
        verbose_name=_('Author'),
        default=False,
    )
    profile_photo = models.ImageField(
        upload_to='user_photos',
        verbose_name=_('Profile photo'),
    )
    first_name = models.CharField(
        verbose_name=_('First name'),
        max_length=20,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name=_('Last name'),
        max_length=20,
        blank=True,
    )
    birthday = models.DateField(
        verbose_name=_('Date of birth'),
        null=True,
    )
    telegram_link = models.URLField(
        verbose_name=_('Telegram profile'),
        blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ('email',)
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique user'
            )
        ]

    def __str__(self):
        return self.username[:15]

    @property
    def is_author(self):
        return self.author


class ConfirmationCode(models.Model):
    """Model users code."""
    email = models.EmailField(
        max_length=320,
        verbose_name='Email',
        unique=True,
        validators=[ASCIIUsernameValidator()],
        help_text=_('Enter the email.'),
        error_messages={
            'unique': _('User with such an email already exists'),
        },
    )
    confirmation_code = models.CharField(
        verbose_name=_('Confirmation code'),
        max_length=100,
    )


class UserConnection(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Выберите из списка пользователя',
    )

    class Meta:
        abstract = True


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name=_('Subscriber'),
        help_text=_('Who is following the user')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='is_subscribed',
        verbose_name=_('Author'),
        help_text=_('Who the user is following')
    )

    class Meta:
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')
        constraints = (
            models.CheckConstraint(
                name='constraint_self_follow',
                check=~models.Q(subscriber=models.F('author'))
            ),
            models.UniqueConstraint(
                name='follower_and_folowwing_have_unique_relationships',
                fields=('subscriber', 'author')
            )
        )


class UserConfirmationCode(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='code_owner',
    )
    confirmation_code = models.CharField(
        max_length=100,
    )
    is_confirmed = models.BooleanField(
        default=False,
    )
