from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image as pilimage
from io import BytesIO
from .models import UploadedImage
from django.utils import timezone


def generate_links(
    image_sizes, image, original_width, original_height, title, author):
    file_links = []
    format = image.format
    for size in image_sizes:
        if size.width and size.height:
            expected_size = (size.width, size.height)
        elif size.width:
            new_height = int(original_height * (size.width / original_width))
            expected_size = (size.width, new_height)
        elif size.height:
            new_width = int(original_width * (size.height / original_height))
            expected_size = (new_width, size.height)
        else:
            expected_size = (original_width, original_height)

        resized_img = image.resize(expected_size, pilimage.LANCZOS)

        output_stream = BytesIO()
        resized_img.save(output_stream, format=format)

        image_file = InMemoryUploadedFile(
            output_stream,
            None,
            "resized_image.jpg",
            f"image/{format.lower()}",
            output_stream.tell(),
            None,
        )

        image_model = UploadedImage(title=title, author=author, upload_image=image_file)

        image_model.save()
        file_links.append(image_model.upload_image.url)

    return file_links


def check_expiriation_status(image):
    current_time = timezone.now()
    time_added = image.add_time
    time_to_expire_secounds = image.time_to_expire
    time_difference = current_time - time_added

    return time_difference.total_seconds() > time_to_expire_secounds
