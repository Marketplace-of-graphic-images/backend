from random import randint

from django.conf import settings as django_settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework.request import Request

from .encryption_str import hash_value
from users.models import ConfirmationCode

User = get_user_model()

SUBJECT_EMAIL = "Confirmation code for 'domen_name'"
TEXT_EMAIL = "Enter the confirmation code on the site to activate your account"


def create_six_digit_confirmation_code() -> str:
    """The make_token method generates a six-digit confirmation
    code and returns it.
    """
    return str(randint(1000000, 9999999))[1::]


def send_email_with_confirmation_code(request: Request) -> None:
    """
    Sends an email with a confirmation code to the provided email address.

    Parameters:
    - request: The request object containing the email address.
    """
    email = request.data.get("email")
    confirmation_code = create_confirmation_code(request)
    send_mail(
        SUBJECT_EMAIL,
        f"{TEXT_EMAIL} = {confirmation_code}",
        django_settings.EMAIL_BACKEND_NAME,
        (email,),
        fail_silently=False,
    )


def create_confirmation_code(request: Request) -> str:
    """
    Generates a confirmation code for a user based on the provided
    request data.

    Args:
        request (Request): The HTTP request object containing the user's
        username and email.

    Returns:
        str: The generated confirmation code.
    """
    email = request.data.get("email")
    confirmation_code = create_six_digit_confirmation_code()
    confirmation_obj, _ = ConfirmationCode.objects.get_or_create(
        email=email,
    )
    confirmation_obj.confirmation_code = hash_value(confirmation_code)
    confirmation_obj.save()
    return confirmation_code


def user_confirmation_code_to_db(code: str, user: User) -> None:
    """The method encrypts confirmation code and writes it to the database."""
    user.code_owner.all().delete()
    user.code_owner.create(confirmation_code=hash_value(code))
