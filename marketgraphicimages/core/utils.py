import io
from random import randint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from google_images_search import GoogleImagesSearch
from passlib.context import CryptContext
from PIL import Image
from rest_framework.request import Request

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
        settings.EMAIL_BACKEND_NAME,
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
        int: The generated confirmation code.
    """
    email = request.data.get("email")
    confirmation_code = create_six_digit_confirmation_code()
    confirmation_obj, _ = ConfirmationCode.objects.get_or_create(
        email=email,
    )
    confirmation_obj.confirmation_code = hash_value(confirmation_code)
    confirmation_obj.save()
    return confirmation_code


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_value(value: str) -> str:
    """Hashing value using multiple algorithms."""
    return pwd_context.hash(value)


def verify_value(value: str, hash_value: str) -> bool:
    """Verifying value using multiple algorithms."""
    return pwd_context.verify(value, hash_value)


def user_confirmation_code_to_db(code: str, user: User) -> None:
    """The method encrypts confirmation code and writes it to the database."""
    user.code_owner.all().delete()
    user.code_owner.create(confirmation_code=hash_value(code))


def get_img_from_google(search_name: str = 'Природа'):

    API_KEY = ''
    PROJECT_CX = ''
    gis = GoogleImagesSearch(API_KEY, PROJECT_CX)

    _search_params = {
        'q': search_name,
        'num': 10,
    }

    gis.search(search_params=_search_params)
    return gis


def show_img(gis):
    my_bytes_io = io.BytesIO()

    for image in gis.results():
        my_bytes_io.seek(0)
        raw_image_data = image.get_raw_data()
        image.copy_to(my_bytes_io, raw_image_data)
        image.copy_to(my_bytes_io)
        my_bytes_io.seek(0)
        temp_img = Image.open(my_bytes_io)
        temp_img.show()
