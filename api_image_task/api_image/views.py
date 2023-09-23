import shortuuid
from PIL import Image as pilimage
from io import BytesIO
from django.http import JsonResponse, FileResponse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework import status

from .models import UploadedImage, ExpiringLinks
from .serializers import (
    UploadedImageSerializer,
    AddRetriveExpiringLinksSerializer,
    RetriveListImageSerializer,
)
from .utils import calculate_seconds_left, change_image_size, create_random_name


class AddImageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UploadedImageSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file_links = []
        author = request.user.client
        serializer.validated_data["author"] = author
        uploaded_image = serializer.validated_data.get("upload_image")
        title = serializer.validated_data.get("title")
        pillow_image = pilimage.open(uploaded_image)
        format = pillow_image.format
        image_sizes = author.account_type.image_sizes.all()

        if author.account_type.orginal_image_acces:
            random_name = create_random_name(title=title, format_name=format)
            uploaded_image.name = random_name

            serializer.save()
            file_links.append(
                {
                    "id": serializer.instance.id,
                    "original url": serializer.instance.upload_image.url,
                }
            )

        for size in image_sizes:
            resized_pillow_img = change_image_size(
                pillow_image=pillow_image, height=size.height, width=size.width
            )
            buffer = BytesIO()
            resized_pillow_img.save(buffer, format=format)
            random_name = create_random_name(size=size, title=title, format_name=format)
            new_image_instance = UploadedImage(
                upload_image=SimpleUploadedFile(random_name, buffer.getvalue()),
                author=author,
                title=title,
            )
            new_image_instance.save()
            file_links.append(
                {
                    "id": new_image_instance.id,
                    "url": new_image_instance.upload_image.url,
                }
            )

        data = {"title": title, "urls": file_links}
        return JsonResponse(data, status=status.HTTP_201_CREATED)


class UserImageView(RetrieveAPIView):
    serializer_class = RetriveListImageSerializer

    def get_queryset(self):
        image_id = self.kwargs["pk"]
        return UploadedImage.objects.filter(id=image_id)


class UserImagesListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RetriveListImageSerializer

    def get_queryset(self):
        user = self.request.user
        return UploadedImage.objects.filter(author=user.id)


class AddRetriveExpiringLinks(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        time_link_acces = request.user.client.account_type.time_limited_link_acces
        if not time_link_acces:
            return JsonResponse(
                {"account_type": "Your account lacks sufficient permissions"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AddRetriveExpiringLinksSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uuid_str = str(shortuuid.uuid())
        url = reverse("time-expiring", args=[uuid_str])
        serializer.validated_data["expiring_link"] = uuid_str
        secound_to_expire = serializer.validated_data["time_to_expire"]
        serializer.save()

        data = {"url": url, "secound_to_expire": secound_to_expire}

        return JsonResponse(data, status=status.HTTP_201_CREATED)

    def get(self, request, link_name):
        link_object = get_object_or_404(ExpiringLinks, expiring_link=link_name)
        time_left = calculate_seconds_left(
            add_time=link_object.add_time, time_to_expire=link_object.time_to_expire
        )

        if time_left != 0:
            image_id = link_object.image_id.id

            image_object = get_object_or_404(UploadedImage, id=image_id)

            image_file = image_object.upload_image.path
            return FileResponse(open(image_file, "rb"))

        else:
            return JsonResponse(
                {"link_status": "link already expired"}, status=status.HTTP_410_GONE
            )
