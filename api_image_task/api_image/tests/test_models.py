from django.test import TestCase
from django.contrib.auth.models import User
from ..models import (
    ThumbnailDimensions,
    AccountTier,
    ClientAccount,
    UploadedImage,
    ExpiringLinks,
)
from django.core.exceptions import ValidationError
from PIL import Image as pilimage
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone


class ThumbnailDimensionsTestCase(TestCase):
    def test_missing_dimensions(self):
        with self.assertRaises(ValidationError):
            thumbnail = ThumbnailDimensions()
            thumbnail.full_clean()

    def test_negative_height(self):
        with self.assertRaises(ValidationError):
            thumbnail = ThumbnailDimensions(height=-1, width=200)
            thumbnail.full_clean()

    def test_negative_width(self):
        with self.assertRaises(ValidationError):
            thumbnail = ThumbnailDimensions(height=100, width=-1)
            thumbnail.full_clean()

    def test_both_dimensions_negative(self):
        with self.assertRaises(ValidationError):
            thumbnail = ThumbnailDimensions(height=-1, width=-1)
            thumbnail.full_clean()

    def test_zero_dimensions(self):
        with self.assertRaises(ValidationError):
            thumbnail = ThumbnailDimensions(height=0, width=0)
            thumbnail.full_clean()

    def test_valid_str_representation(self):
        thumbnail = ThumbnailDimensions(height=100, width=None)
        self.assertEqual(str(thumbnail), "any x 100")

    def test_valid_str_representation_width(self):
        thumbnail = ThumbnailDimensions(height=None, width=200)
        self.assertEqual(str(thumbnail), "200 x any")

    def test_valid_str_representation_both(self):
        thumbnail = ThumbnailDimensions(height=300, width=400)
        self.assertEqual(str(thumbnail), "300x400")


class AccountTierTestCase(TestCase):
    def setUp(self):
        self.thumbnail_dim1 = ThumbnailDimensions.objects.create(height=100, width=200)
        self.thumbnail_dim2 = ThumbnailDimensions.objects.create(height=300, width=400)

    def test_valid_account_tier(self):
        account_tier = AccountTier.objects.create(
            name="Premium", orginal_image_acces=True, time_limited_link_acces=True
        )
        account_tier.image_sizes.add(self.thumbnail_dim1)

        self.assertEqual(account_tier.name, "Premium")
        self.assertTrue(account_tier.orginal_image_acces)
        self.assertTrue(account_tier.time_limited_link_acces)
        self.assertEqual(account_tier.image_sizes.count(), 1)

    def test_multiple_image_sizes(self):
        account_tier = AccountTier.objects.create(
            name="Pro", orginal_image_acces=True, time_limited_link_acces=False
        )
        account_tier.image_sizes.add(self.thumbnail_dim1, self.thumbnail_dim2)

        self.assertEqual(account_tier.name, "Pro")
        self.assertTrue(account_tier.orginal_image_acces)
        self.assertFalse(account_tier.time_limited_link_acces)
        self.assertEqual(account_tier.image_sizes.count(), 2)

    def test_empty_image_sizes(self):
        with self.assertRaises(ValidationError):
            account_tier = AccountTier(
                name="Free", orginal_image_acces=False, time_limited_link_acces=False
            )
            account_tier.save()
            account_tier.full_clean()


class ClientAccountTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.thumbnail_dim = ThumbnailDimensions.objects.create(height=100, width=None)

        self.account_tier = AccountTier.objects.create(
            name="Test Tier", orginal_image_acces=True, time_limited_link_acces=False
        )
        self.account_tier.image_sizes.add(self.thumbnail_dim)

    def test_create_client_account(self):
        client_account = ClientAccount.objects.create(
            user=self.user, account_type=self.account_tier
        )

        retrieved_client_account = ClientAccount.objects.get(pk=client_account.pk)

        self.assertEqual(retrieved_client_account.user, self.user)
        self.assertEqual(retrieved_client_account.account_type, self.account_tier)

    def test_client_account_str_method(self):
        client_account = ClientAccount.objects.create(
            user=self.user, account_type=self.account_tier
        )

        expected_str = f"Owner: {self.user} Account type: {self.account_tier}"

        self.assertEqual(str(client_account), expected_str)


class UploadedImageTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")

        self.thumbnail_dim = ThumbnailDimensions.objects.create(height=100, width=None)

        self.account_tier = AccountTier.objects.create(
            name="Test Tier", orginal_image_acces=True, time_limited_link_acces=False
        )
        self.account_tier.image_sizes.add(self.thumbnail_dim)

        self.client_account = ClientAccount.objects.create(
            user=self.user, account_type=self.account_tier
        )

    def create_image(self, width=100, height=100):
        image = pilimage.new("RGB", (width, height))
        image_io = BytesIO()
        image.save(image_io, format="JPEG")
        image_io.seek(0)
        return SimpleUploadedFile(
            "test_image.jpg", image_io.read(), content_type="image/jpeg"
        )

    def test_create_uploaded_image(self):
        image_io = self.create_image()
        uploaded_image = UploadedImage.objects.create(
            title="Test Image",
            author=self.client_account,
            upload_image=image_io,
        )

        retrieved_uploaded_image = UploadedImage.objects.get(pk=uploaded_image.pk)

        self.assertEqual(retrieved_uploaded_image.title, "Test Image")
        self.assertEqual(retrieved_uploaded_image.author, self.client_account)

    def test_uploaded_image_str_method(self):
        image_io = self.create_image()
        uploaded_image = UploadedImage.objects.create(
            title="Test Image",
            author=self.client_account,
            upload_image=image_io,
        )

        expected_str = f"Image title: Test Image by {self.user}"

        self.assertEqual(str(uploaded_image), expected_str)


class ExpiringLinksTestCase(TestCase):
    def setUp(self):
        self.client_account = ClientAccount.objects.create(
            user=User.objects.create(username="testuser"),
            account_type=AccountTier.objects.create(
                name="Test Tier",
                orginal_image_acces=True,
                time_limited_link_acces=False,
            ),
        )

        self.uploaded_image = UploadedImage.objects.create(
            title="Test Image",
            author=self.client_account,
            upload_image=self.create_image(),
        )

    def create_image(self, width=100, height=100):
        image = pilimage.new("RGB", (width, height))
        image_io = BytesIO()
        image.save(image_io, format="JPEG")
        image_io.seek(0)

        return SimpleUploadedFile(
            "test_image.jpg", image_io.read(), content_type="image/jpeg"
        )

    def test_create_expiring_link(self):
        expiring_link = ExpiringLinks.objects.create(
            image_id=self.uploaded_image,
            time_to_expire=3600,
            expiring_link="randomlink123",
        )

        retrieved_expiring_link = ExpiringLinks.objects.get(pk=expiring_link.pk)

        self.assertEqual(retrieved_expiring_link.image_id, self.uploaded_image)
        self.assertEqual(retrieved_expiring_link.time_to_expire, 3600)
        self.assertEqual(retrieved_expiring_link.expiring_link, "randomlink123")


def test_seconds_left(self):
    current_time = timezone.now()

    future_expiring_link = ExpiringLinks.objects.create(
        image_id=self.uploaded_image,
        time_to_expire=3600,
        add_time=current_time - timezone.timedelta(minutes=30),
        expiring_link="randomlink123",
    )

    seconds_left = future_expiring_link.secounds_left()

    self.assertGreaterEqual(seconds_left, 0)

    past_expiring_link = ExpiringLinks.objects.create(
        image_id=self.uploaded_image,
        time_to_expire=3600,
        add_time=current_time - timezone.timedelta(hours=2),
        expiring_link="anotherlink123",
    )

    seconds_left = past_expiring_link.secounds_left()

    self.assertLessEqual(seconds_left, 0)
