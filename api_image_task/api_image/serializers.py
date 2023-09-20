from rest_framework import serializers
from .models import ImageModel, ExpiringLinks
from PIL import Image as pilimage


class ImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ["title", "upload_image"]

    def validate_upload_image(self, value):
        image = pilimage.open(value)
        if image.format.lower() not in ["png", "jpeg"]:
            raise serializers.ValidationError(
                {"upload_image": "Unsupported image format"}
            )
        return value


class ExpiringLinksSerializer(serializers.ModelSerializer):
    image = serializers.CharField()

    class Meta:
        model = ExpiringLinks
        fields = ["image", "time_to_expire"]

    def validate_image(self, value):
        print("jestem w validatorze")
        try:
            image = value.split("media/")[1]
            if image.endswith("/"):
                image = image[:-1]
                print("jestem po czyszczeniu linku", image)
        except IndexError:
            raise ValueError({"image link": "Wrong link, please copy your image link"})

        try:
            image_pk = ImageModel.objects.get(upload_image=image)
            return image_pk

        except ImageModel.DoesNotExist:
            return serializers.ValidationError(
                {"image": "Image on this adress does not exist"}
            )
