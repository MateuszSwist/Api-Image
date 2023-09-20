import string
import secrets
from io import BytesIO
from PIL import Image as pilimage

from django.utils import timezone
from django.http import JsonResponse, FileResponse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import ImagexAccount, ImageModel, ExpiringLinks
from .serializers import ImageModelSerializer, ExpiringLinksSerializer


def generate_links(
    image_sizes, image, original_width, original_height, title, author, format="JPEG"
):
    file_links = []
    format = image.format
    for size in image_sizes:
        if size.width and size.height:
            expected_size = (size.width, size.height)
        elif size.width:
            new_height = int(original_height * (size.width / original_width))
            expected_size = (size.width, new_height)
        elif size.height:
            new_width = int(original_width * (size.height / original_height))
            expected_size = (new_width, size.height)
        else:
            expected_size = (original_width, original_height)

        resized_img = image.resize(expected_size, pilimage.LANCZOS)

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

        image_model = ImageModel(title=title, author=author, upload_image=image_file)

        image_model.save()
        file_links.append(image_model.upload_image.url)

    return file_links


def check_expiriation_status(image):
    current_time = timezone.now()
    time_added = image.add_time
    time_to_expire_secounds = image.time_to_expire
    time_difference = current_time - time_added

    if time_difference.total_seconds() > time_to_expire_secounds:
        return False
    else:
        return True


class AddImageView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_links = []

        try:
            account_tier = request.user.user.account_type
        except ImagexAccount.DoesNotExist:
            return JsonResponse(
                {"message": "Account does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ImageModelSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        title = serializer.validated_data["title"]

        author = request.user.user
        serializer.validated_data["author"] = author
        # create link if can have original link
        if account_tier.orginal_image_link:
            serializer.save()
            file_links.append(serializer.instance.upload_image.url)

        uploaded_image = serializer.validated_data.get("upload_image")
        image = pilimage.open(uploaded_image)

        original_width, original_height = image.size
        image_sizes = account_tier.image_size.all()
        # create all available sizes of image links
        resized_links = generate_links(
            image_sizes, image, original_width, original_height, title, author
        )
        file_links.extend(resized_links)

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
        images = ImageModel.objects.filter(author=user)

        if images.exists():
            serializer = ImageModelSerializer(images, many=True)
            return JsonResponse({"data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(
                {"message": f"Not found any images of {user}"},
                status=status.HTTP_404_NOT_FOUND,
            )


class AddLinkToEspiringLinksView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = self.request.user.user
        serializer = ExpiringLinksSerializer(data=request.data)

        if serializer.is_valid():
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
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoadExpiringLinkView(APIView):
    def get(self, request, expiring_link):
        expiring_link = f"time-link/{expiring_link}"
        link = get_object_or_404(ExpiringLinks, expiring_link=expiring_link)

        if check_expiriation_status(link):
            image_file = link.image.upload_image.path
            return FileResponse(open(image_file, "rb"))
        else:
            return JsonResponse(
                {"message": "Sorry, Link already expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
