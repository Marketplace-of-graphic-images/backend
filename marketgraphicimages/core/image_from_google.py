import io

from django.conf import settings
from google_images_search import GoogleImagesSearch
from PIL import Image


def get_img_from_google(search_name: str = 'Природа', num_images: int = 10):

    API_KEY = settings.GOOGLE_API_KEY
    PROJECT_CX = settings.GOOGLE_PROJECT_CX
    gis = GoogleImagesSearch(API_KEY, PROJECT_CX)

    _search_params = {
        'q': search_name,
        'num': num_images,
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
