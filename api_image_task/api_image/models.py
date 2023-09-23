from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from .utils import calculate_seconds_left


class ThumbnailDimensions(models.Model):
    height = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)

    def clean(self):
        if self.height is None and self.width is None:
            raise ValidationError("At least one thumbnail dimension must be provided.")

        if self.height is not None and self.height < 1:
            raise ValidationError("Height must be greater than or equal to 1.")

        if self.width is not None and self.width < 1:
            raise ValidationError("Width must be greater than or equal to 1.")

    def __str__(self):
        if self.height is None:
            return f"{self.width}w x anyh"
        elif self.width is None:
            return f"anyw x {self.height}h"
        else:
            return f"{self.height}h x {self.width}w"


class AccountTier(models.Model):
    name = models.CharField(max_length=64)
    orginal_image_acces = models.BooleanField(default=False)
    time_limited_link_acces = models.BooleanField(default=False)
    image_sizes = models.ManyToManyField(ThumbnailDimensions)

    def clean(self):
        if not self.image_sizes.exists():
            raise ValidationError("At least one image size must be selected.")

    def __str__(self):
        return self.name


class ClientAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client")
    account_type = models.ForeignKey(
        AccountTier, on_delete=models.CASCADE, related_name="account_type"
    )

    def __str__(self):
        return f"Owner: {self.user} Account type: {self.account_type}"


class UploadedImage(models.Model):
    add_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=128)
    author = models.ForeignKey(
        ClientAccount, on_delete=models.CASCADE, related_name="client_account"
    )
    upload_image = models.ImageField()

    def __str__(self):
        return f"Image title: {self.title} by {self.author.user}"


class ExpiringLinks(models.Model):
    add_time = models.DateTimeField(auto_now_add=True)
    image_id = models.ForeignKey(
        UploadedImage, on_delete=models.CASCADE, related_name="original"
    )
    time_to_expire = models.IntegerField()

    expiring_link = models.CharField(max_length=256, null=True, blank=True)

    def secounds_left(self):
        return calculate_seconds_left(
            add_time=self.add_time, time_to_expire=self.time_to_expire
        )

    def __str__(self):
        return f"Line expire in: {self.time_to_expire} sec, owner: {self.owner}."
