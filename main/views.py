from copy import deepcopy

from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from rest_framework import status, serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from scms.worker import process_image
from .models import ScmsUser, ScmsComplaint
from .serializers import ScmsUserSerializer, ScmsComplaintSerializer


# Create your views here.
# views.py


class RegisterView(APIView):
    def post(self, request):
        serializer = ScmsUserSerializer(
            data={
                "u_username": request.data.get("username"),
                "u_password": request.data.get("password"),
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Success", "uid": serializer.data["id"]},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    def post(self, request):
        uname = request.data.get("username")
        password = request.data.get("password")

        if not (uname and password):
            return Response(
                {"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(ScmsUser, u_username=uname)
        # match password
        if not check_password(password, user.u_password):
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(
            {
                "message": "Welcome",
                "uid": user.id,
                "user": ScmsUserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


# Repeat the process for other views (root, history, download, upload, file).
class HistoryView(APIView):
    def post(self, request):
        uid = request.data.get("uid")
        if uid is None:
            return Response({"results": []}, status=status.HTTP_200_OK)

        try:
            complaints = ScmsComplaint.objects.filter(u_id=uid).order_by("-c_datetime")
            complaint_ids = ScmsComplaintSerializer(
                complaints, many=True, context={"request": request}
            ).data
            return Response({"results": complaint_ids}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DownloadView(APIView):
    def post(self, request):
        c_id = request.data.get("c_id")
        complaint = get_object_or_404(ScmsComplaint, c_id=c_id)
        serializer = ScmsComplaintSerializer(complaint, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminComplaintViewPermissionMixin(APIView):
    def check_permissions(self, request):
        print("checking permissions")
        user_id = self.kwargs.get("uid")
        user = get_object_or_404(ScmsUser, id=user_id)
        print("user found")
        if not user.is_admin:
            raise PermissionDenied("You are not authorized to perform this action")


class AdminComplaintView(AdminComplaintViewPermissionMixin):
    def get(self, request: Request, *args, **kwargs):
        self.check_permissions(request)
        filters = request.GET
        complaints = ScmsComplaint.objects.all().order_by("-c_datetime")
        if "verified" in filters:
            complaints = complaints.filter(c_verified=filters["verified"]).order_by(
                "-c_datetime"
            )
        if "resolved" in filters:
            complaints = complaints.filter(c_resolved=filters["resolved"]).order_by(
                "-c_datetime"
            )
        serializer = ScmsComplaintSerializer(
            complaints, many=True, context={"request": request}
        )
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)


class AdminComplaintUpdateView(AdminComplaintViewPermissionMixin):
    def put(self, request: Request, *args, **kwargs):
        self.check_permissions(request)
        complaint_id = self.kwargs.get("complaint_id")
        print("getting complaint")
        complaint = get_object_or_404(ScmsComplaint, id=complaint_id)
        prev_complaint = deepcopy(complaint)
        serializer = ScmsComplaintSerializer(
            complaint, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        user = get_object_or_404(ScmsUser, id=self.kwargs["uid"])
        # c_resolved changed
        if obj.c_resolved != prev_complaint.c_resolved:
            print("c_resolved changed")
            obj.resolver = user if obj.c_resolved == "y" else None
            obj.save()
        if obj.c_verified != prev_complaint.c_verified:
            print("c_verified changed")
            obj.verifier = user if obj.c_verified == "y" else None
            # remove resolve status
            obj.c_resolved = "n"
            obj.resolver = None
            obj.save()
        return Response(
            {
                "message": "Updated",
                "result": ScmsComplaintSerializer(
                    obj, context={"request": request}
                ).data,
            },
            status=status.HTTP_200_OK,
        )


class CreateComplaintView(APIView):
    def post(self, request: Request):
        if "image_data" not in request.FILES:
            raise serializers.ValidationError({"message": "image_data is required"})
        file = request.FILES.get("image_data")
        img_name = file.name
        img_data = file.read()
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")
        datetime = request.data.get("datetime")
        uid = request.data.get("userid")
        title = request.data.get("title")
        if not uid:
            return Response(
                {"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
            )

        complaint_data = {
            "u_id": uid,
            "c_in_image": file,
            "c_verified": "n",
            "c_resolved": "n",
            "c_lat": latitude,
            "c_long": longitude,
            "c_title": title,
            "c_class": [],
        }

        serializer = ScmsComplaintSerializer(
            data=complaint_data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        process_image.delay(instance.id)
        return Response(
            {"message": "Upload Done", "result": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class GetUserInfoView(APIView):
    def post(self, request):
        uid = request.data.get("uid")
        if uid is None:
            raise serializers.ValidationError({"message": "uid is required"})
        user = get_object_or_404(ScmsUser, id=uid)
        serializer = ScmsUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
