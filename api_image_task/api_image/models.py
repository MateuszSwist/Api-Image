from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class ThumbnailDimensions(models.Model):
    height = models.IntegerField()
    width = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Height:{self.height} x width:{self.width}."


class AccountTier(models.Model):
    name = models.CharField(max_length=64)
    orginal_image_acces = models.BooleanField(default=False)
    time_limited_link_acces = models.BooleanField(default=False)
    image_sizes = models.ManyToManyField(ThumbnailDimensions)

    def __str__(self):
        return self.name


class ClientAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client")
    account_type = models.OneToOneField(
        AccountTier, on_delete=models.CASCADE, related_name="account_type"
    )

    def __str__(self):
        return f"Owner: {self.user} Account type: {self.account_type}."


class UploadedImage(models.Model):
    add_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=128)
    author = models.ForeignKey(ClientAccount, on_delete=models.CASCADE)
    upload_image = models.ImageField()

    def __str__(self):
        return f" Image title: {self.title} by {self.author.user}"


class ExpiringLinks(models.Model):
    add_time = models.DateTimeField(auto_now_add=True)
    image = models.ForeignKey(
        UploadedImage, on_delete=models.CASCADE, related_name="orginal"
    )
    time_to_expire = models.IntegerField(
        validators=[
            MinValueValidator(300, message="Min sec value is 300"),
            MaxValueValidator(30000, message="Max sec value is 30000"),
        ]
    )

    expiring_link = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return f"Line expire in: {self.time_to_expire} sec, owner: {self.owner}."
