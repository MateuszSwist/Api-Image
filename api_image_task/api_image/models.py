from django.db import models
from django.contrib.auth.models import User


class ImageHeigth(models.Model):

    height = models.IntegerField()

class AccountTier(models.Model):
    name = models.CharField(max_length=64)
    orginal_image_link = models.BooleanField(default=False)
    time_limited_link = models.BooleanField(default=False)
    image_size = models.ManyToManyField(ImageHeigth)

    def __str__(self):
        return self.name

class ImagexAccount(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_type = models.OneToOneField(AccountTier, on_delete=models.DO_NOTHING)