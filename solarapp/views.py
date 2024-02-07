from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .serializers import InstallerProfileSerializer, UserProfileSerializer, UserProfileSignInSerializer
from .models import Installer, UserProfile
from rest_framework import viewsets
from rest_framework.response import Response

from rest_framework import status
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password,make_password

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate

# Create your views here.

from .serializers import InstallerSignInSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    UserModel View.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()

# class MyObtainTokenPairView(TokenObtainPairView):
#     permission_classes = (AllowAny,)
#     serializer_class = MyTokenObtainPairSerializer


# @api_view(['POST'])
# def signup(request):
#     username = request.data.get('username')
#     password = request.data.get('password')

#     if not username or not password:
#         return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

#     user = User.objects.create_user(username=username, password=password)
#     user.save()

#     return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

# @api_view(['POST'])
# def login(request):
#     username = request.data.get('username')
#     password = request.data.get('password')

#     user = authenticate(username=username, password=password)
#     if user:
#         refresh = RefreshToken.for_user(user)
#         return Response({
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#         }, status=status.HTTP_200_OK)
#     else:
#         return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def user_list(request):
#     users = User.objects.all()
#     user_data = [{'id': user.id, 'username': user.username} for user in users]
#     return Response(user_data)

@api_view(['POST'])
def installer_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if Installer.objects.filter(email=email).exists():
            response = {'error': 'E-mail already in use'}
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)
        elif Installer.objects.filter(username=username).exists():
            response = {'error': f'Username "{username}" already in use'}
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)

        # Hash the password before saving
        hashed_password = make_password(password)

        serializer = InstallerProfileSerializer(data=request.data)
        if serializer.is_valid():
            # Set the hashed password in the serializer data
            serializer.validated_data['password'] = hashed_password
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def installer_signin(request):
    if request.method == 'POST':
        serializer = InstallerSignInSerializer(data=request.data)
        if serializer.is_valid():
            installer = serializer.validated_data['installer']

            # Authentication successful, generate JWT token
            refresh = RefreshToken.for_user(installer)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def add_user(request, installer_id):
    if request.method == 'POST':
        try:
            installer = Installer.objects.get(pk=installer_id)
        except Installer.DoesNotExist:
            return Response({'error': 'Installer not found'}, status=status.HTTP_404_NOT_FOUND)

        username = request.POST['username']
        email = request.POST['email']
        if UserProfile.objects.filter(email=email).exists():
            response = {
                'Error':'E-mail Already Used'
            }
            return JsonResponse(response)
        elif UserProfile.objects.filter(username=username).exists():
            response = {
                'Error':f'Username [{username}] Already Used'
            }
            return JsonResponse(response)
        
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            # Check if the user already has an installer
            if UserProfile.objects.filter(email=serializer.validated_data['email']).exists():
                return Response({'error': 'User already assigned to an installer'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save(installer=installer)
            # serializer.save()
            # installer.users.add(serializer.instance)  # Assuming you have a ManyToManyField named 'users' in your Installer model
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def user_signin(request):
    if request.method == 'POST':
        serializer = UserProfileSignInSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Authentication successful, generate JWT token
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_user_initial_password(request, installer_id, user_id):
    if request.method == 'GET':
        try:
            installer = Installer.objects.get(pk=installer_id)
            user = UserProfile.objects.get(pk=user_id, installer=installer)
        except Installer.DoesNotExist:
            return Response({'error': 'Installer not found'}, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User not found or not associated with the installer'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'initial_password': user.password}, status=status.HTTP_200_OK)


# 

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def user_change_password(request):
    if request.method == 'PUT':
        user = request.user
        print(request.auth,request.data,request.user,sep='\n')
        # if not user.is_authenticated:
        #     return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        # Fetch UserProfile instance
        try:
            user_profile = UserProfile.objects.get(username=user.username)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the old password matches the current password of the user
        if not check_password(old_password, user_profile.password):
            return Response({'error': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the user's password
        user_profile.set_password(new_password)
        user_profile.save()

        return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)

    
    
