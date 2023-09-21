import string
import secrets

from PIL import Image as pilimage


from django.http import JsonResponse, FileResponse

from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import UploadedImage, ExpiringLinks
from .serializers import UploadedImageSerializer, ExpiringLinksSerializer
from .utils import generate_links, check_expiriation_status


class AddImageView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_links = []

        serializer = UploadedImageSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_image = serializer.validated_data.get("upload_image")
        image = pilimage.open(uploaded_image)
        format = image.format.lower()

        if format not in ["png", "jpeg"]:
            return JsonResponse(
                {"upload_image": "Unsupported image format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        title = serializer.validated_data["title"]
        author = request.user.client
        serializer.validated_data["author"] = author
        # create link if can have original link
        account_tier = request.user.client.account_type
        if account_tier.orginal_image_acces:
            serializer.save()
            file_links.append(serializer.instance.upload_image.url)

        original_width, original_height = image.size
        image_sizes = account_tier.image_sizes.all()
        # create all available sizes of image links
        resized_links = generate_links(
            image_sizes, image, original_width, original_height, title, author
        )
        file_links.extend(resized_links)

        data = {"file_links": file_links}
        return JsonResponse(data, status=status.HTTP_201_CREATED)

class UserImagesView(ListAPIView):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_class = [IsAuthenticated]
    serializer_class = UploadedImageSerializer
    
    def get_queryset(self):
        user = self.request.user.client
        return UploadedImage.objects.filter(author=user)


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
