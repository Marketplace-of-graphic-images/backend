import io

from django.conf import settings
from django.core.files.images import ImageFile
from google_images_search import GoogleImagesSearch
from PIL import Image


def get_img_from_google(search_name: str = 'Природа', num_images: int = 10):
    """
    Fetches images from Google Images using the Google Images Search API.

    Args:
        search_name (str, optional): The search query for images.
        num_images (int, optional): The number of images to fetch.

    Returns:
        GoogleImagesSearch: An instance of the GoogleImagesSearch class
        with search results.
    """
    if (
        num_images < 1 or not isinstance(search_name, str)
        or not isinstance(num_images, int)
    ):
        raise ValueError("Invalid input data")

    if (
        settings.GOOGLE_API_KEY is None
        or settings.GOOGLE_PROJECT_CX is None
    ):
        raise ValueError("Invalid Google API key or project CX")

    API_KEY = settings.GOOGLE_API_KEY
    PROJECT_CX = settings.GOOGLE_PROJECT_CX
    gis = GoogleImagesSearch(API_KEY, PROJECT_CX)

    _search_params = {
        'q': search_name,
        'num': num_images,
    }

    gis.search(search_params=_search_params)
    return gis


def get_image_data(image) -> tuple:
    """
    Extracts image data such as the file name and format
    from a Google Images Search result.

    Args:
        image: A Google Images Search result image.

    Returns:
        tuple: A tuple containing the file name (str) and image format (str).
    """
    splitted_name = image.url.split('/')[-1]
    img_format = splitted_name.split('.')[-1]
    img_format = 'JPEG' if img_format.lower() == 'jpg' else img_format
    return splitted_name, img_format


def open_image(image) -> Image:
    """
    Opens and returns an image from a Google Images Search result.

    Args:
        image: A Google Images Search result image.

    Returns:
        Image: An Image object representing the image.
    """
    my_bytes_io = io.BytesIO()
    my_bytes_io.seek(0)
    raw_image_data = image.get_raw_data()
    image.copy_to(my_bytes_io, raw_image_data)
    image.copy_to(my_bytes_io)
    my_bytes_io.seek(0)
    return Image.open(my_bytes_io)


def get_img_file(image) -> ImageFile:
    """
    Saves an image from a Google Images Search result to a BytesIO stream
    and returns it as an ImageFile.

    Args:
        image: A Google Images Search result image.

    Returns:
        ImageFile: An ImageFile object representing the image in a BytesIO.
    """
    my_bytes_io = io.BytesIO()
    temp_img = open_image(image)
    splitted_name, img_format = get_image_data(image)
    temp_img.save(my_bytes_io, format=img_format)
    return ImageFile(my_bytes_io, name=splitted_name)
