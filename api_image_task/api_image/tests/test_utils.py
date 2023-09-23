from datetime import timedelta
from io import BytesIO
from PIL import Image as pilimage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from ..models import ThumbnailDimensions
from ..utils import calculate_seconds_left, change_image_size, create_random_name


class ChangeImageSizeTest(TestCase):
    def create_image(self, width=100, height=100):
        image = pilimage.new("RGB", (width, height))
        image_io = BytesIO()
        image.save(image_io, format="JPEG")
        image_io.seek(0)
        return SimpleUploadedFile(
            "test_image.jpg", image_io.read(), content_type="image/jpeg"
        )

    def test_change_image_size_with_width(self):
        original_image = self.create_image(width=200, height=100)
        pillow_image = pilimage.open(original_image)
        new_width = 150

        resized_image = change_image_size(pillow_image, width=new_width)

        self.assertEqual(resized_image.size, (new_width, 75))

    def test_change_image_size_with_height(self):
        original_image = self.create_image(width=200, height=100)
        pillow_image = pilimage.open(original_image)
        new_height = 50

        resized_image = change_image_size(pillow_image, height=new_height)

        self.assertEqual(resized_image.size, (100, new_height))

    def test_change_image_size_with_both_width_and_height(self):
        original_image = self.create_image(width=200, height=100)
        pillow_image = pilimage.open(original_image)
        new_width = 150
        new_height = 50

        resized_image = change_image_size(
            pillow_image, width=new_width, height=new_height
        )

        self.assertEqual(resized_image.size, (new_width, new_height))

    def test_change_image_size_with_no_dimensions(self):
        original_image = self.create_image(width=200, height=100)
        pillow_image = pilimage.open(original_image)

        resized_image = change_image_size(pillow_image)

        self.assertEqual(resized_image.size, (200, 100))


class CrateRandomNameTest(TestCase):
    def assert_size_in_name(self, size_str, random_name):
        parts = random_name.split("-")
        name = parts[1].split(".")[0]
        self.assertTrue(size_str in name)

    def test_create_random_name_with_all_parameters(self):
        size = ThumbnailDimensions(height=100, width=200)
        title = "TestTitle"
        format_name = "jpeg"
        size_in_name = "100x200"
        random_name = create_random_name(size, title, format_name)

        self.assertTrue(title in random_name)
        self.assertTrue(format_name in random_name)
        self.assert_size_in_name(size_in_name, random_name)

    def test_create_random_name_with_size_and_format(self):
        size = ThumbnailDimensions(height=100, width=200)
        format_name = "jpeg"
        size_in_name = "100x200"
        random_name = create_random_name(size=size, format_name=format_name)

        self.assertTrue(format_name in random_name)
        self.assert_size_in_name(size_in_name, random_name)

    def test_create_random_name_with_title_and_format(self):
        title = "TestTitle"
        format_name = "jpeg"
        random_name = create_random_name(title=title, format_name=format_name)

        self.assertTrue(title in random_name)
        self.assertTrue(format_name in random_name)

    def test_create_random_name_with_size_only(self):
        size = ThumbnailDimensions(height=100, width=200)
        size_in_name = "100x200"
        random_name = create_random_name(size=size)

        self.assert_size_in_name(size_in_name, random_name)

    def test_create_random_name_with_format_only(self):
        format_name = "jpeg"
        random_name = create_random_name(format_name=format_name)

        self.assertTrue(format_name in random_name)

    def test_create_random_name_includes_random_string(self):
        random_name = create_random_name()

        parts = random_name.split("-")
        random_string = parts[0]
        self.assertEqual(len(random_string), 10)


class CalculateSecondsLeftTest(TestCase):
    def test_seconds_left_when_still_valid(self):
        add_time = timezone.now() - timedelta(hours=1)
        time_to_expire = 7200
        expected_seconds_left = 3600

        result = calculate_seconds_left(add_time, time_to_expire)

        self.assertEqual(result, expected_seconds_left)

    def test_seconds_left_when_already_expired(self):
        add_time = timezone.now() - timedelta(hours=2)
        time_to_expire = 3600
        expected_seconds_left = 0
        result = calculate_seconds_left(add_time, time_to_expire)
        self.assertEqual(result, expected_seconds_left)

    def test_seconds_left_when_expires_now(self):
        add_time = timezone.now() - timedelta(hours=1)
        time_to_expire = 3600
        expected_seconds_left = 0
        result = calculate_seconds_left(add_time, time_to_expire)
        self.assertEqual(result, expected_seconds_left)

    def test_seconds_left_when_no_time_left(self):
        add_time = timezone.now() - timedelta(hours=3)
        time_to_expire = 3600
        expected_seconds_left = 0
        result = calculate_seconds_left(add_time, time_to_expire)
        self.assertEqual(result, expected_seconds_left)

    def test_seconds_left_with_zero_time_to_expire(self):
        add_time = timezone.now() - timedelta(hours=1)
        time_to_expire = 0
        expected_seconds_left = 0
        result = calculate_seconds_left(add_time, time_to_expire)
        self.assertEqual(result, expected_seconds_left)
