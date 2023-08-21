import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from users.models import ConfirmationCode
User = get_user_model()

SUBJECT_EMAIL = "Confirmation code for 'domen_name'"
TEXT_EMAIL = "Enter the confirmation code on the site to activate your account"

def send_email_with_confirmation_code(request):
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
        settings.EMAIL_BACKEND_NAME,
        (email,),
        fail_silently=False,
    )


def create_confirmation_code(request):
    """
    Generates a confirmation code for a user based on the provided
    request data.

    Args:
        request (Request): The HTTP request object containing the user's
        username and email.

    Returns:
        str: The generated confirmation code.

    Raises:
        Http404: If the user with the given username and email is not found.
    """
    # username = request.data.get("username")
    email = request.data.get("email")
    # user = get_object_or_404(User, username=username, email=email)
    confirmation_obj = ConfirmationCode.objects.get_or_create(email=email)
    confirmation_code = str(random.randint(100000, 999999))
    confirmation_obj.code = confirmation_code
    confirmation_obj.save()
    # user.confirmation_code = confirmation_code
    # user.save()
    return confirmation_code
