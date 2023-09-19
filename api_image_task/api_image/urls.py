from django.urls import path
from .views import AddImageView

urlpatterns = [path("add-image/", AddImageView.as_view(), name="add-image")]
