import io
import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from google_images_search import GoogleImagesSearch
from PIL import Image

User = get_user_model()


def send_email_with_confirmation_code(request):
    """
    Sends an email with a confirmation code to the provided email address.

    Parameters:
    - request: The request object containing the email address.
    """
    email = request.data.get("email")
    confirmation_code = create_confirmation_code(request)
    send_mail(
        "System messege",
        f"confirmation_code = {confirmation_code}",
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
    username = request.data.get("username")
    email = request.data.get("email")
    user = get_object_or_404(User, username=username, email=email)
    confirmation_code = str(random.randint(100000, 999999))
    user.confirmation_code = confirmation_code
    user.save()
    return confirmation_code


def get_img_from_google(search_name: str = 'Природа'):

    API_KEY = 'AIzaSyA8uUxNe7Bzg_GvPTfIX0g48KsHUYD53fM'
    PROJECT_CX = '13bf908ff1a6242d2'
    gis = GoogleImagesSearch(API_KEY, PROJECT_CX)
    my_bytes_io = io.BytesIO()

    _search_params = {
        'q': search_name,
        'num': 10,
    }

    gis.search(search_params=_search_params)

    for image in gis.results():
        my_bytes_io.seek(0)
        raw_image_data = image.get_raw_data()
        image.copy_to(my_bytes_io, raw_image_data)
        image.copy_to(my_bytes_io)
        my_bytes_io.seek(0)
        temp_img = Image.open(my_bytes_io)
        temp_img.show()
