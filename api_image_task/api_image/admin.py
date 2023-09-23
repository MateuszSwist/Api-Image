from django.contrib import admin
from .models import (
    ThumbnailDimensions,
    AccountTier,
    ClientAccount,
    UploadedImage,
    ExpiringLinks,
)
from .utils import calculate_seconds_left


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
    list_display = ["add_time", "seconds_left", "expiring_link", "image_id"]

    def seconds_left(self, obj):
        return calculate_seconds_left(
            add_time=obj.add_time, time_to_expire=obj.time_to_expire
        )
