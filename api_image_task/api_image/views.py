import string
from rest_framework.views import APIView
import secrets
from django.utils import timezone
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import ImagexAccount, ImageModel, ExpiringLinks
from django.http import JsonResponse
from rest_framework import status
from .serializers import (
    ImageModelSerializer,
    ExpiringLinksSerializer,
)
from PIL import Image as pilimage
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import FileResponse


def check_espiriation_status(image):
    current_time = timezone.now()
    time_added = image.add_time
    time_to_expire_secounds = image.time_to_expire
    time_difference = current_time - time_added

    if time_difference.total_seconds() > time_to_expire_secounds:
        return False
    else:
        return True


class AddImageView(APIView):
    # permission/authentication
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_links = []

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
        title = serializer.validated_data["title"]
        # adding author
        author = request.user.user
        serializer.validated_data["author"] = author

        # activites depend on account tier:
        # 1.orginal link
        if account_tier.orginal_image_link:
            serializer.save()
            file_links.append(serializer.instance.upload_image.url)

        # 2. size compilation:
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

            output_stream = BytesIO()
            resized_img.save(output_stream, format=format)
            image_file = InMemoryUploadedFile(
                output_stream,
                None,
                "resized_image.jpg",
                f"image/{format.lower()}",
                output_stream.tell(),
                None,
            )

            image_model = ImageModel(
                title=title, author=author, upload_image=image_file
            )
            image_model.save()
            file_links.append(image_model.upload_image.url)

        data = {"file_links": file_links}
        return JsonResponse(data, status=status.HTTP_201_CREATED)


class ImageView(APIView):
    def get(self, request, image_name):
        try:
            image = ImageModel.objects.get(upload_image=image_name)
            image_file = image.upload_image.path
            return FileResponse(open(image_file, "rb"))
        except ImageModel.DoesNotExist:
            return JsonResponse(
                {"message": "Image not found"}, status=status.HTTP_404_NOT_FOUND
            )


class UserImagesView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = self.request.user.user
        try:
            images = ImageModel.objects.filter(author=user)
            serializer = ImageModelSerializer(images, many=True)
            return JsonResponse({"data": serializer.data}, status=status.HTTP_200_OK)
        except ImageModel.DoesNotExist:
            return JsonResponse(
                {"message": f"Not found any images of {self.user}"},
                status=status.HTTP_404_NOT_FOUND,
            )


class AddLinkToEspiringLinksView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = self.request.user.user
        serializer = ExpiringLinksSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        second_to_expire = serializer.validated_data["time_to_expire"]
        image_pk = serializer.validated_data["image"]
        random_string = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(10)
        )
        link = f"time-link/{random_string}"
        serializer.save(owner=user, expiring_link=link, image=image_pk)

        data = {
            "second to expire": second_to_expire,
            "expiring link": link,
        }
        return JsonResponse(data, status=status.HTTP_201_CREATED)


class LoadExpiringLinkView(APIView):
    def get(self, request, expiring_link):
        try:
            expiring_link = "time-link/" + expiring_link
            link = ExpiringLinks.objects.get(expiring_link=expiring_link)

        except ExpiringLinks.DoesNotExist:
            return JsonResponse(
                {"message": "Image not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if check_espiriation_status(link):
            image = link.image
            image_file = image.upload_image.path
            return FileResponse(open(image_file, "rb"))
        else:
            return JsonResponse({"message": "Sorry, Link already expired"})
