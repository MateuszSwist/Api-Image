import os
import tempfile
from PIL import Image as pilimage

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User

from ..models import UploadedImage, ClientAccount, AccountTier, ThumbnailDimensions
from ..serializers import (
    UploadedImageSerializer,
    RetriveListImageSerializer,
    AddRetriveExpiringLinksSerializer,
)


class UploadedImageSerializerTests(TestCase):
    def setUp(self):
        self.valid_image = pilimage.new("RGB", (100, 100))
        self.valid_image_path = tempfile.NamedTemporaryFile(
            suffix=".jpeg", delete=False
        ).name
        self.valid_image.save(self.valid_image_path)

    def tearDown(self):
        os.remove(self.valid_image_path)

    def test_validate_upload_image_valid_format(self):
        image_file = open(self.valid_image_path, "rb")
        image_data = SimpleUploadedFile("valid_image.jpeg", image_file.read())

        data = {
            "title": "Test Image",
            "upload_image": image_data,
        }

        serializer = UploadedImageSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_upload_image_invalid_format(self):
        invalid_image_path = tempfile.NamedTemporaryFile(
            suffix=".gif", delete=False
        ).name
        invalid_image = pilimage.new("RGB", (100, 100))
        invalid_image.save(invalid_image_path)
        invalid_image_file = open(invalid_image_path, "rb")
        invalid_image_data = SimpleUploadedFile(
            "invalid_image.gif", invalid_image_file.read()
        )

        data = {
            "title": "Test Image",
            "upload_image": invalid_image_data,
        }

        serializer = UploadedImageSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("upload_image", serializer.errors)
        self.assertEqual(
            serializer.errors["upload_image"][0], "Unsupported image format"
        )

    def test_validate_upload_image_invalid_image(self):
        invalid_image_path = tempfile.NamedTemporaryFile(
            suffix=".txt", delete=False
        ).name
        with open(invalid_image_path, "w") as file:
            file.write("This is not an image")
        invalid_image_file = open(invalid_image_path, "rb")
        invalid_image_data = SimpleUploadedFile(
            "non_image.txt", invalid_image_file.read()
        )

        data = {
            "title": "Test Image",
            "upload_image": invalid_image_data,
        }

        serializer = UploadedImageSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("upload_image", serializer.errors)


class RetriveListImageSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

        self.thumbnail_dimensions = ThumbnailDimensions.objects.create(
            height=100, width=100
        )

        self.account_tier = AccountTier.objects.create(
            name="Basic",
            orginal_image_acces=True,
            time_limited_link_acces=True,
        )
        self.account_tier.image_sizes.add(self.thumbnail_dimensions)

        self.client_account = ClientAccount.objects.create(
            user=self.user, account_type=self.account_tier
        )

        self.image = UploadedImage.objects.create(
            title="Test Image",
            author=self.client_account,
            upload_image="test_image.jpg",
        )

    def test_serialize_image(self):
        serializer = RetriveListImageSerializer(self.image)
        expected_data = {
            "id": self.image.id,
            "title": "Test Image",
            "upload_image": self.image.upload_image.url,
        }
        self.assertEqual(serializer.data, expected_data)

    def tearDown(self):
        for uploaded_image in UploadedImage.objects.all():
            if os.path.isfile(uploaded_image.upload_image.path):
                os.remove(uploaded_image.upload_image.path)


class AddRetriveExpiringLinksSerializerTests(TestCase):
    def setUp(self):
        self.thumbnail_dimensions = ThumbnailDimensions.objects.create(
            width=100, height=200
        )

        self.account_tier = AccountTier.objects.create(
            name="Basic Tier",
            orginal_image_acces=True,
            time_limited_link_acces=True,
        )
        self.account_tier.image_sizes.add(self.thumbnail_dimensions)

        self.user = User.objects.create_user("testuser")

        self.client_account = ClientAccount.objects.create(
            user=self.user,
            account_type=self.account_tier,
        )

        self.uploaded_image = UploadedImage.objects.create(
            title="Test Image",
            author=self.client_account,
            upload_image="test_image.jpg",
        )

    def test_invalid_time_to_expire_lower_limit(self):
        data = {"image_id": self.uploaded_image.id, "time_to_expire": 299}
        serializer = AddRetriveExpiringLinksSerializer(data=data)

        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_invalid_time_to_expire_upper_limit(self):
        data = {"image_id": self.uploaded_image.id, "time_to_expire": 30001}
        serializer = AddRetriveExpiringLinksSerializer(data=data)

        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_valid_time_to_expire(self):
        data = {"image_id": self.uploaded_image.id, "time_to_expire": 1000}
        serializer = AddRetriveExpiringLinksSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def tearDown(self):
        for uploaded_image in UploadedImage.objects.all():
            if os.path.isfile(uploaded_image.upload_image.path):
                os.remove(uploaded_image.upload_image.path)
