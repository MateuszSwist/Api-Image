import string
import secrets

from PIL import Image as pilimage

from django.http import JsonResponse, FileResponse
from io import BytesIO

from django.core.files import File
from rest_framework.views import APIView

from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import UploadedImage, ExpiringLinks
from .serializers import UploadedImageSerializer
from .utils import check_expiriation_status, change_image_size, create_random_name


class AddImageView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
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
            serializer.save()
            file_links.append(
                {
                    "orginal": serializer.instance.upload_image.url,
                }
            )

        for size in image_sizes:
            resized_pillow_img = change_image_size(
                pillow_image=pillow_image, height=size.height, width=size.width
            )
            buffer = BytesIO()
            resized_pillow_img.save(buffer, format=format)
            random_name = create_random_name(size=size, title=title, format_name=format)
            serializer.instance.upload_image.save(random_name, buffer)
            serializer.instance.save()
            file_links.append(serializer.instance.upload_image.url)

        data = {"title": title, "urls": file_links}
        return JsonResponse(data, status=status.HTTP_201_CREATED)


class UserImagesView(ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_class = [IsAuthenticated]
    serializer_class = UploadedImageSerializer

    def get_queryset(self):
        user = self.request.user.client
        return UploadedImage.objects.filter(author=user)


# class AddRetriveExpiringLinkView




# class AddExpiringLinkView(APIView):
#     authentication_classes = [SessionAuthentication, BasicAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = self.request.user.user
#         serializer = ExpiringLinksSerializer(data=request.data)

#         if serializer.is_valid():
#             second_to_expire = serializer.validated_data["time_to_expire"]
#             image_pk = serializer.validated_data["image"]
#             random_string = "".join(
#                 secrets.choice(string.ascii_letters + string.digits) for _ in range(10)
#             )
#             link = f"time-link/{random_string}"

#             serializer.save(owner=user, expiring_link=link, image=image_pk)

#             data = {
#                 "second to expire": second_to_expire,
#                 "expiring link": link,
#             }
#             return JsonResponse(data, status=status.HTTP_201_CREATED)
#         else:
#             return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class LoadExpiringLinkView(APIView):
#     def get(self, request, expiring_link):
#         expiring_link = f"time-link/{expiring_link}"
#         link = get_object_or_404(ExpiringLinks, expiring_link=expiring_link)

#         if check_expiriation_status(link):
#             image_file = link.image.upload_image.path
#             return FileResponse(open(image_file, "rb"))
#         else:
#             return JsonResponse(
#                 {"message": "Sorry, Link already expired"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
