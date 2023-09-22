from PIL import Image as pilimage
from rest_framework import serializers
from .models import UploadedImage, ExpiringLinks


class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ["title", "upload_image"]

    def validate_upload_image(self, value):
        try:
            image = pilimage.open(value)
            format = image.format.lower()
            if format not in ["png", "jpeg"]:
                raise serializers.ValidationError("Unsupported image format")
        except pilimage.UnidentifiedImageError:
            raise serializers.ValidationError()

        return value


class RetriveListImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ["id", "title", "upload_image"]


class AddRetriveExpiringLinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpiringLinks
        fields = ["image_id", "time_to_expire"]

    def validate_time_to_expire(self, value):
        if not 300 <= value <= 30000:
            raise serializers.ValidationError(
                "Time to expire must be between 300 and 30000 seconds."
            )
        return value
