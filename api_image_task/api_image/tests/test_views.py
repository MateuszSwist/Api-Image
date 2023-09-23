import io
import os
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from ..models import (
    ClientAccount,
    AccountTier,
    ThumbnailDimensions,
    UploadedImage,
    ExpiringLinks,
)
from ..serializers import RetriveListImageSerializer


class AddImageViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.account_tier = AccountTier.objects.create(
            name="Test Tier", orginal_image_acces=True
        )
        self.thumbnail_dimensions = ThumbnailDimensions.objects.create(
            height=100, width=100
        )
        self.account_tier.image_sizes.add(self.thumbnail_dimensions)
        self.client_account = ClientAccount.objects.create(
            user=self.user, account_type=self.account_tier
        )
        self.image = self.create_test_image()

    def create_test_image(self):
        image = Image.new("RGB", (100, 100))
        image_io = io.BytesIO()
        image.save(image_io, format="JPEG")
        return SimpleUploadedFile("test_image.jpg", image_io.getvalue())

    def test_add_image(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("add-image")
        data = {
            "title": "Test Image",
            "upload_image": self.image,
        }

        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UploadedImage.objects.count(), 2)

        expected_data = {
            "title": "Test Image",
            "urls": [
                {
                    "id": response.json()["urls"][0]["id"],
                    "original url": response.json()["urls"][0]["original url"],
                },
                {
                    "id": response.json()["urls"][1]["id"],
                    "url": response.json()["urls"][1]["url"],
                },
            ],
        }

        self.assertEqual(response.json(), expected_data)

    def test_add_image_unauthenticated(self):
        url = reverse("add-image")
        data = {
            "title": "Test Image",
            "upload_image": self.image,
        }

        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_image_invalid_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("add-image")
        data = {
            "title": "",
            "upload_image": self.image,
        }

        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UploadedImage.objects.count(), 0)

    def test_add_image_no_image(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("add-image")
        data = {
            "title": "Test Image",
        }

        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UploadedImage.objects.count(), 0)

    def tearDown(self):
        for filename in os.listdir(settings.MEDIA_ROOT):
            if "Test_Image" in filename:
                os.remove(os.path.join(settings.MEDIA_ROOT, filename))


class UserImageViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.thumbnail_dimensions = ThumbnailDimensions.objects.create(
            height=100, width=100
        )
        self.account_tier = AccountTier.objects.create(
            name="Test Tier", orginal_image_acces=True, time_limited_link_acces=False
        )
        self.account_tier.image_sizes.add(self.thumbnail_dimensions)
        self.client_account = ClientAccount.objects.create(
            user=self.user, account_type=self.account_tier
        )
        self.image = self.create_test_image()
        self.uploaded_image = UploadedImage.objects.create(
            title="Test Image",
            author=self.client_account,
            upload_image=self.image,
        )
        self.serializer = RetriveListImageSerializer(instance=self.uploaded_image)

    def create_test_image(self):
        image = Image.new("RGB", (100, 100))
        image_io = io.BytesIO()
        image.save(image_io, format="JPEG")
        return SimpleUploadedFile("test_image.jpg", image_io.getvalue())

    def test_get_user_image_authenticated(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("user-image-detail", kwargs={"pk": self.uploaded_image.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.uploaded_image.id)
        self.assertEqual(response.data["title"], self.uploaded_image.title)

    def test_get_user_image_unauthenticated(self):
        url = reverse("user-image-detail", kwargs={"pk": self.uploaded_image.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.uploaded_image.id)
        self.assertEqual(response.data["title"], self.uploaded_image.title)

    def test_get_nonexistent_user_image(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("user-image-detail", kwargs={"pk": 999999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserImagesListViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.thumbnail_dimensions = ThumbnailDimensions.objects.create(
            height=100, width=100
        )
        self.account_tier = AccountTier.objects.create(
            name="Test Tier", orginal_image_acces=True, time_limited_link_acces=False
        )
        self.account_tier.image_sizes.add(self.thumbnail_dimensions)
        self.client_account = ClientAccount.objects.create(
            user=self.user, account_type=self.account_tier
        )
        self.image1 = self.create_test_image()
        self.image2 = self.create_test_image()
        self.uploaded_image1 = UploadedImage.objects.create(
            title="Test Image 1",
            author=self.client_account,
            upload_image=self.image1,
        )
        self.uploaded_image2 = UploadedImage.objects.create(
            title="Test Image 2",
            author=self.client_account,
            upload_image=self.image2,
        )
        self.serializer1 = RetriveListImageSerializer(instance=self.uploaded_image1)
        self.serializer2 = RetriveListImageSerializer(instance=self.uploaded_image2)

    def create_test_image(self):
        image = Image.new("RGB", (100, 100))
        image_io = io.BytesIO()
        image.save(image_io, format="JPEG")
        return SimpleUploadedFile("test_image.jpg", image_io.getvalue())

    def test_get_user_images_authenticated(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("user-images-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["id"], self.uploaded_image1.id)
        self.assertEqual(response.data[0]["title"], self.uploaded_image1.title)
        self.assertEqual(response.data[0]["id"], self.uploaded_image1.id)
        self.assertEqual(response.data[0]["title"], self.uploaded_image1.title)

        self.assertEqual(response.data[1]["id"], self.uploaded_image2.id)
        self.assertEqual(response.data[1]["title"], self.uploaded_image2.title)
        self.assertEqual(response.data[1]["id"], self.uploaded_image2.id)
        self.assertEqual(response.data[1]["title"], self.uploaded_image2.title)

    def test_get_user_images_unauthenticated(self):
        url = reverse("user-images-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_images_empty(self):
        UploadedImage.objects.filter(author=self.client_account).delete()

        self.client.force_authenticate(user=self.user)
        url = reverse("user-images-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def tearDown(self):
        for filename in os.listdir(settings.MEDIA_ROOT):
            if filename.startswith("test_image"):
                os.remove(os.path.join(settings.MEDIA_ROOT, filename))


class AddRetriveExpiringLinksTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

        thumbnail_dimensions = ThumbnailDimensions.objects.create(height=100, width=100)
        account_tier = AccountTier.objects.create(
            name="Test Tier", orginal_image_acces=True, time_limited_link_acces=True
        )
        account_tier.image_sizes.add(thumbnail_dimensions)

        client_account = ClientAccount.objects.create(
            user=self.user, account_type=account_tier
        )

        image = self.create_test_image()
        self.uploaded_image = UploadedImage.objects.create(
            title="Test Image",
            author=client_account,
            upload_image=image,
        )

    def create_test_image(self):
        image = Image.new("RGB", (100, 100))
        image_io = io.BytesIO()
        image.save(image_io, format="JPEG")
        return SimpleUploadedFile("test_image.jpg", image_io.getvalue())

    def test_serializer_validation_error(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("time-expiring")
        data = {
            "image_id": self.uploaded_image.id,
            "time_to_expire": "invalid_value",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_expiring_link_authenticated(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("time-expiring")
        data = {
            "image_id": self.uploaded_image.id,
            "time_to_expire": 3600,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("url", response.json())
        self.assertIn("secound_to_expire", response.json())

        link_name = response.json()["url"].split("/")[-1]
        expiring_link = ExpiringLinks.objects.get(expiring_link=link_name)
        self.assertEqual(expiring_link.time_to_expire, data["time_to_expire"])
        self.assertEqual(expiring_link.image_id.id, data["image_id"])

    def test_create_expiring_link_unauthenticated(self):
        url = reverse("time-expiring")
        data = {
            "image_id": self.uploaded_image.id,
            "time_to_expire": 3600,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_expiring_link_valid(self):
        link_object = ExpiringLinks.objects.create(
            image_id=self.uploaded_image, time_to_expire=3600, expiring_link=1
        )
        link_name = link_object.expiring_link
        url = reverse("time-expiring", args=[link_name])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_expiring_link_expired(self):
        past_time = timezone.now() - timezone.timedelta(seconds=7200)
        link_object = ExpiringLinks.objects.create(
            add_time=past_time,
            image_id=self.uploaded_image,
            time_to_expire=0,
            expiring_link=1,
        )
        link_name = link_object.expiring_link
        url = reverse("time-expiring", args=[link_name])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_410_GONE)
        self.assertEqual(response.json()["link_status"], "link already expired")

    def tearDown(self):
        for filename in os.listdir(settings.MEDIA_ROOT):
            if filename.startswith("test_image"):
                file_path = os.path.join(settings.MEDIA_ROOT, filename)

    def test_create_expiring_link_basic_account(self):
        self.user.client.account_type.time_limited_link_acces = False
        self.client.force_authenticate(user=self.user)

        url = reverse("time-expiring")
        data = {
            "image_id": self.uploaded_image.id,
            "time_to_expire": 3600,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.json(),
            {"account_type": "Your account lacks sufficient permissions"},
        )


class MediaConfigTestCase(TestCase):
    def test_media_root_exists(self):
        self.assertTrue(os.path.exists(settings.MEDIA_ROOT))

    def test_media_url(self):
        self.assertTrue(settings.MEDIA_URL)

    def test_media_url_starts_with_slash(self):
        self.assertTrue(settings.MEDIA_URL.startswith("/"))
