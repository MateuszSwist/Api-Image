from django.urls import path
from .views import (
    AddImageView,
    ImageView,
    UserImagesView,
    AddLinkToEspiringLinksView,
    LoadExpiringLinkView,
)

urlpatterns = [
    path("add-image/", AddImageView.as_view(), name="add-image"),
    path("media/<str:image_name>/", ImageView.as_view(), name="image-detail"),
    path("user-images/", UserImagesView.as_view(), name="user-images"),
    path(
        "add-expiring-link/",
        AddLinkToEspiringLinksView.as_view(),
        name="add-expiring-link",
    ),
    path(
        "time-link/<str:expiring_link>/",
        LoadExpiringLinkView.as_view(),
        name="expiring-link",
    ),
]
