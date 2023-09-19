from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class ThumbnailDimentions(models.Model):
    height = models.IntegerField()
    width = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Height:{self.height}, width:{self.width}."


class AccountTier(models.Model):
    name = models.CharField(max_length=64)
    orginal_image_link = models.BooleanField(default=False)
    time_limited_link = models.BooleanField(default=False)
    image_size = models.ManyToManyField(ThumbnailDimentions)

    def __str__(self):
        return self.name


class ImagexAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user")
    account_type = models.OneToOneField(
        AccountTier, on_delete=models.DO_NOTHING, related_name="account_type"
    )

    def __str__(self):
        return f"Owner: {self.user} Account type: {self.account_type}."


class ImageModel(models.Model):
    add_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=128)
    author = models.ForeignKey(ImagexAccount, on_delete=models.CASCADE)
    upload_image = models.ImageField()

    def __str__(self):
        return f" Image title: {self.title} by {self.author} added at {self.add_time}."


class ExpiringLinks(models.Model):
    add_time = models.DateTimeField(auto_now_add=True)
    image = models.ForeignKey(ImageModel, on_delete=models.CASCADE)
    time_to_expire = models.IntegerField(
        validators=[
            MinValueValidator(300, message="Min sec value is 300"),
            MaxValueValidator(30000, message="Max sec value is 30000"),
        ]
    )
    owner = models.ForeignKey(
        ImagexAccount, on_delete=models.CASCADE, related_name="owner"
    )

    def __str__(self):
        return f"Line expire in: {self.time_to_expire} sec, owner: {self.owner}."
