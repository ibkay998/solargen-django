from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .serializers import (
    InstallerProfileSerializer,
    InstallerProfileViewSerializer,
    UserProfileSerializer,
    UserProfileSignInSerializer,
    InstallerSignUpSerializer,
    InstallerAddUserSerializer,
    ChangePasswordSerializer,
)
from .models import Installer, UserProfile, CustomUser
from rest_framework import viewsets
from rest_framework.response import Response

from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password, make_password

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate

# Create your views here.

from .serializers import InstallerSignInSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    UserModel View.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()


@swagger_auto_schema(method="post", request_body=InstallerSignUpSerializer)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def installer_signup(request):
    if request.method == "POST":
        serializer_signup = InstallerSignUpSerializer(data=request.data)
        if serializer_signup.is_valid():
            # Hash the password before saving

            hashed_password = make_password(
                serializer_signup.validated_data.get("password")
            )
            latitude = serializer_signup.validated_data.get("latitude")
            longitude = serializer_signup.validated_data.get("longitude")
            address_found = serializer_signup.validated_data.get("address_found")
            address_provided = serializer_signup.validated_data.get("address_provided")
            company_name = serializer_signup.validated_data.get("company_name")
            contact_number = serializer_signup.validated_data.get("contact_number")
            full_name = serializer_signup.validated_data.get("full_name")
            other_names = serializer_signup.validated_data.get("other_names")

            serializer_profile = InstallerProfileSerializer(data=request.data)
            # Set the hashed password in the serializer_profile data

            if serializer_profile.is_valid():
                serializer_profile.validated_data["password"] = hashed_password
                serializer_profile.validated_data.update(
                    {
                        "latitude": latitude,
                        "longitude": longitude,
                        "address_found": address_found,
                        "address_provided": address_provided,
                        "company_name": company_name,
                        "contact_number": contact_number,
                        "full_name": full_name,
                        "other_names": other_names,
                    }
                )

                serializer_profile.save()
                return Response(serializer_profile.data, status=status.HTTP_201_CREATED)
            return Response(
                serializer_profile.errors, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer_signup.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="post", request_body=InstallerSignInSerializer)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def installer_signin(request):
    if request.method == "POST":
        serializer_signin = InstallerSignInSerializer(data=request.data)
        if serializer_signin.is_valid():
            installer = serializer_signin.validated_data["installer"]
            # Authentication successful, generate JWT token
            refresh = RefreshToken.for_user(installer)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                serializer_signin.errors, status=status.HTTP_400_BAD_REQUEST
            )


@swagger_auto_schema(
    method="post",
    request_body=InstallerAddUserSerializer,
    manual_parameters=[
        openapi.Parameter(
            "Authorization",
            openapi.IN_HEADER,
            description="Description of custom header",
            type=openapi.TYPE_STRING,
        )
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_user(request):
    if request.method == "POST":
        installer = request.user
        installer_instance = Installer.objects.get(username=installer.username)
        # Pass the installer to the serializer during initialization
        serializer_add_user = InstallerAddUserSerializer(
            data=request.data, context={"installer": installer_instance}
        )
        if serializer_add_user.is_valid():
            # Save the user profile using the serializer's save method
            serializer_add_user.save()

            return Response("User Successfully created", status=status.HTTP_201_CREATED)

        return Response(serializer_add_user.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    request_body=ChangePasswordSerializer,
    manual_parameters=[
        openapi.Parameter(
            "Authorization",
            openapi.IN_HEADER,
            description="Description of custom header",
            type=openapi.TYPE_STRING,
        )
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def installer_change_password(request):
    if request.method == "POST":
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            # Fetch UserProfile instance
            try:
                user_profile = Installer.objects.get(username=user.username)
            except Installer.DoesNotExist:
                return Response(
                    {"error": "Installer not found"}, status=status.HTTP_404_NOT_FOUND
                )

            # print(serializer.validated_data['new_password'], user_profile.password)
            # Check if the old password matches the current password of the user
            if not check_password(
                serializer.validated_data["old_password"], user_profile.password
            ):
                return Response(
                    {"error": "Invalid old password"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update the user's password
            user_profile.set_password(serializer.validated_data["new_password"])
            user_profile.save()

            return Response(
                {"message": "Password updated successfully"}, status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter(
            "Authorization",
            openapi.IN_HEADER,
            description="Description of custom header",
            type=openapi.TYPE_STRING,
        )
    ],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def installer_view_profile(request):
    if request.method == "GET":
        serializer = InstallerProfileViewSerializer(data=request.data)
        if serializer.is_valid():
            installer_username = request.user.username
            installer = Installer.objects.get(username=installer_username)

            profile = {
                "Name": installer.full_name,
                "Location": installer.address_found,
                "Company": installer.company_name,
                "Number of Assets": installer.installed_assets,
                "Email Address": installer.email,
                "Contact Number": installer.contact_number,
            }
            return Response(profile, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""
USERS
"""


@swagger_auto_schema(method="post", request_body=UserProfileSignInSerializer)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def user_signin(request):
    if request.method == "POST":
        serializer = UserProfileSignInSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # Authentication successful, generate JWT token
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    request_body=ChangePasswordSerializer,
    manual_parameters=[
        openapi.Parameter(
            "Authorization",
            openapi.IN_HEADER,
            description="Description of custom header",
            type=openapi.TYPE_STRING,
        )
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_change_password(request):
    if request.method == "POST":
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            # Fetch UserProfile instance
            try:
                user_profile = UserProfile.objects.get(username=user.username)
            except UserProfile.DoesNotExist:
                return Response(
                    {"error": "User profile not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # print(serializer.validated_data['new_password'], user_profile.password)
            # Check if the old password matches the current password of the user
            if not check_password(
                serializer.validated_data["old_password"], user_profile.password
            ):
                return Response(
                    {"error": "Invalid old password"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update the user's password
            user_profile.set_password(serializer.validated_data["new_password"])
            user_profile.save()

            return Response(
                {"message": "Password updated successfully"}, status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
