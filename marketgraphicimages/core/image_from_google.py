import io

from django.contrib.auth import get_user_model
from google_images_search import GoogleImagesSearch
from PIL import Image

User = get_user_model()

SUBJECT_EMAIL = "Confirmation code for 'domen_name'"
TEXT_EMAIL = "Enter the confirmation code on the site to activate your account"


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
