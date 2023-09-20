from PIL import Image as pilimage
from rest_framework import serializers
from .models import ImageModel, ExpiringLinks


class ImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ["title", "upload_image"]

    def validate_upload_image(self, value):
        try:
            image = pilimage.open(value)
            format = image.format.lower()
        except Exception as e:
            raise serializers.ValidationError(
                {"upload_image": f"Unable to open the image: {str(e)}"}
            )

        if format not in ["png", "jpeg"]:
            raise serializers.ValidationError(
                {"upload_image": "Unsupported image format"}
            )

        return value


from rest_framework import serializers
from .models import ExpiringLinks, ImageModel


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
            image_pk = ImageModel.objects.get(upload_image__iendswith=image)
        except ImageModel.DoesNotExist:
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
