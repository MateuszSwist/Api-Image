from django.urls import path
from .views import (
    AddImageView,
    UserImagesView,
    # AddExpiringLinkView,
    # LoadExpiringLinkView,
)
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("add-image/", AddImageView.as_view(), name="add-image"),
    path("user-images/", UserImagesView.as_view({'get': 'list'}), name="user-images"),
    # path(
    #     "add-expiring-link/",
    #     AddExpiringLinkView.as_view(),
    #     name="add-expiring-link",
    # ),
    # path(
    #     "time-link/<str:expiring_link>/",
    #     LoadExpiringLinkView.as_view(),
    #     name="expiring-link",)
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
