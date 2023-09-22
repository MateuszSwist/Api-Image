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


def create_random_name(size=None, title=None, format_name=None):
    name = ""
    if title:
        name += title
    if size:
        if size.height:
            name += str(size.height)
        if size.width:
            name + "x" + str(size.width)

    if format_name:
        file_format = str(format_name).lower()

    random_string = "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(10)
    )

    return f"{random_string}-{name}.{file_format}"


def calculate_seconds_left(add_time, time_to_expire):
    current_time = timezone.now()
    time_difference = current_time - add_time
    seconds_difference = int(time_difference.total_seconds())
    secounds_left = time_to_expire - seconds_difference

    return max(secounds_left, 0)
