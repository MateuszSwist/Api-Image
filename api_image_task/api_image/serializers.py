from PIL import Image as pilimage
from rest_framework import serializers
from .models import UploadedImage, ExpiringLinks


class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ["title", "upload_image"]


class ExpiringLinksSerializer(serializers.ModelSerializer):
    image = serializers.CharField()

    class Meta:
        model = ExpiringLinks
        fields = ["image", "time_to_expire"]

    def validate_image(self, value):
        try:
            image = value.split("media/")[1].rstrip("/")
        except IndexError:
            raise serializers.ValidationError(
                {"image link": "Wrong link, please copy your image link"}
            )

        try:
            image_pk = UploadedImage.objects.get(upload_image__iendswith=image)
        except UploadedImage.DoesNotExist:
            raise serializers.ValidationError(
                {"image": "Image on this address does not exist"}
            )

        return image_pk

    def validate_time_to_expire(self, value):
        if not 300 <= value <= 30000:
            raise serializers.ValidationError(
                "Time to expire must be between 300 and 30000 seconds."
            )
        return value
