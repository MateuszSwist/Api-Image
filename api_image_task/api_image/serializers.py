from rest_framework import serializers
from .models import ImageModel
from PIL import Image as pilimage


class ImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ["title", "upload_image"]

    def validate_upload_image(self, value):
        if value:
            image = pilimage.open(value)
            if image.format.lower() not in ["png", "jpeg"]:
                raise serializers.ValidationError("Unsupported image format")
        return value
