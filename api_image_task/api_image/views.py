from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import ImagexAccount, ImageModel
from django.http import JsonResponse
from rest_framework import status
from .serializers import ImageModelSerializer
from PIL import Image as pilimage
import os


class AddImageView(APIView):
    # permission/authentication
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # getting account tier
        try:
            account_tier = request.user.user.account_type
        except ImagexAccount.DoesNotExist:
            return JsonResponse(
                {"message": "Account does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # getting serializer object
        serializer = ImageModelSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # adding author
        author = request.user.user
        serializer.validated_data["author"] = author

        # activites depend on account tier:
        # 1.orginal link
        if account_tier.orginal_image_link:
            serializer.save()

        # 2. size compilation:
        title = serializer.validated_data["title"]
        uploaded_image = serializer.validated_data.get("upload_image")
        image = pilimage.open(uploaded_image)

        expected_width = None
        expected_height = None
        original_width, original_height = image.size
        image_sizes = account_tier.image_size.all()
        format = image.format

        for size in image_sizes:
            if size.width:
                expected_width = size.width
            if size.height:
                expected_height = size.height

            if expected_height and expected_width:
                resized_img = image.resize(
                    (expected_width, expected_height), pilimage.LANCZOS
                )

            elif expected_height:
                new_width = int(original_width * (expected_height / original_height))
                resized_img = image.resize(
                    (new_width, expected_height), pilimage.LANCZOS
                )

            elif expected_width:
                new_height = int(original_height * (expected_width / original_width))
                resized_img = image.resize(
                    (expected_width, new_height), pilimage.LANCZOS
                )

            resized_img.save("nowy_obraz.jpg")
            serializer.validated_data["upload_image"] = resized_img
            if not serializer.is_valid():
                return JsonResponse(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save()

            # resized_img.save('nowy_obraz.jpg', str(format))
            # resized_image_model = ImageModel(title=title, author=author, upload_image=resized_img)

            # resized_image_model.save()
