import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class InvalidCharactersValidator:
    """
    Validate that the password does not have any invalid characters @, .
    """
    invalid_characters = ('@', ',')

    def validate(self, password, user=None):
        if any(char in password for char in self.invalid_characters):
            raise ValidationError(
                _("This password has invalid characters: @ ,"),
                code="password_invalid_characters_@_,",
            )

    def get_help_text(self):
        return _("Your password must not contain invalid characters.")


class CyrillicLettersValidator:
    """
    Validate that the password does not have any cyrillic letters.
    """
    def validate(self, password, user=None):
        if re.search('[а-яА-Я]', password):
            raise ValidationError(
                _("This password has cyrillic letters"),
                code="password_has_cyrillic_letters",
            )

    def get_help_text(self):
        return _("Your password must not contain cyrillic letters.")


class EasyPasswordValidator:
    """
    Validate that the password has numbers, letters, and special characters.
    """
    pattern = r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[-_!.]).{8,}$'

    def validate(self, password, user=None):
        if not re.match(self.pattern, password):
            raise ValidationError(
                _("Password must contain numbers "
                  "letters and special characters: -_!."),
                code="password_must_contain_numbers_"
                     "letters_and_special_characters",
            )

    def get_help_text(self):
        return _("You password must contain numbers "
                 "letters and special characters")


class MaximumLengthValidator:
    """
    Validate that the password is of a maximum length.
    """

    def __init__(self, max_length=254):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(
                _("This password is too long. It must contain a maximum of "
                  f"{self.max_length} characters."),
                code="password_too_long",
            )

    def get_help_text(self):
        return _("You password must contain a maximum of "
                 f"{self.max_length} characters.")


class TheSamePasswordValidator:
    def validate(self, password, user=None):
        if user and user.check_password(password):
            raise ValidationError(
                _("The new password must be different from the old password."),
                code="the_same_password",
            )

    def get_help_text(self):
        return _("The new password must be different from the old password.")
