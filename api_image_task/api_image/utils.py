from PIL import Image as pilimage
from django.utils import timezone
import string
import secrets


def change_image_size(pillow_image, height=None, width=None):
    original_width, original_height = pillow_image.size
    if width and height:
        expected_size = (width, height)
    elif width:
        new_height = int(original_height * (width / original_width))
        expected_size = (width, new_height)
    elif height:
        new_width = int(original_width * (height / original_height))
        expected_size = (new_width, height)

    resized_img = pillow_image.resize(expected_size, pilimage.LANCZOS)
    return resized_img


def check_expiriation_status(image):
    current_time = timezone.now()
    time_added = image.add_time
    time_to_expire_secounds = image.time_to_expire
    time_difference = current_time - time_added

    return time_difference.total_seconds() > time_to_expire_secounds


def create_random_name(size=None, title=None, format_name=None):
    name = ""
    if title:
        name += title
    if size:
        if size.height:
            name += str(size.height)
        if size.width:
            name + "x" + str(size.width)

    random_string = "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(10)
    )

    if format_name:
        file_format = str(format_name).lower()
    print("file_format:", file_format)

    return f"{random_string}{name}.{file_format}"
