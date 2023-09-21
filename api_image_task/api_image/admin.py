from django.contrib import admin
from django.utils import timezone
from .models import (
    ThumbnailDimensions,
    AccountTier,
    ClientAccount,
    UploadedImage,
    ExpiringLinks,
)


@admin.register(ThumbnailDimensions)
class ThumbnailDimensionsAdmin(admin.ModelAdmin):
    pass


@admin.register(AccountTier)
class AccountTierAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "orginal_image_acces",
        "time_limited_link_acces",
        "display_image_sizes",
    ]

    def display_image_sizes(self, obj):
        return ", ".join([str(size) for size in obj.image_sizes.all()])


@admin.register(ClientAccount)
class ImagexAccountAdmin(admin.ModelAdmin):
    list_display = ["user", "account_type"]


@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ["add_time", "title", "author", "upload_image"]


@admin.register(ExpiringLinks)
class ExpiringLinksAdmin(admin.ModelAdmin):
    list_display = ["add_time", "secounds_left", "expiring_link", "image"]

    def secounds_left(self, obj):
        current_time = timezone.now()
        time_added = obj.add_time
        time_to_expire_secounds = obj.time_to_expire
        time_difference = current_time - time_added
        secounds_left = time_to_expire_secounds - int(time_difference.total_seconds())
        if secounds_left > 0:
            return secounds_left
        else:
            return 0
