from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import (
    AddImageView,
    AddRetriveExpiringLinks,
    UserImageView,
    UserImagesListView,
)

urlpatterns = [
    path("add-image/", AddImageView.as_view(), name="add-image"),
    path("image/<int:pk>/", UserImageView.as_view(), name="user-image-detail"),
    path("images/", UserImagesListView.as_view(), name="user-images-list"),
    path("time-expiring/", AddRetriveExpiringLinks.as_view(), name="time-expiring"),
    path(
        "time-expiring/<str:link_name>",
        AddRetriveExpiringLinks.as_view(),
        name="time-expiring",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
