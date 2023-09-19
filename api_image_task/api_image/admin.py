from django.contrib import admin
from .models import (
    ThumbnailDimentions,
    AccountTier,
    ImagexAccount,
    ImageModel,
    ExpiringLinks,
)


@admin.register(ThumbnailDimentions)
class ThumbnailDimentionsAdmin(admin.ModelAdmin):
    pass


@admin.register(AccountTier)
class AccountTierAdmin(admin.ModelAdmin):
    pass


@admin.register(ImagexAccount)
class ImagexAccountAdmin(admin.ModelAdmin):
    pass


@admin.register(ImageModel)
class ImageModelAdmin(admin.ModelAdmin):
    pass


@admin.register(ExpiringLinks)
class ExpiringLinksAdmin(admin.ModelAdmin):
    pass
