from rest_framework import serializers
from .models import Installer,UserProfile
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password,make_password
from django.contrib.auth import get_user_model
from .models import Installer, UserProfile, CustomUser
from rest_framework.validators import UniqueValidator
from rest_framework import status

# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

#     @classmethod
#     def get_token(cls, user):
#         token = super(MyTokenObtainPairSerializer, cls).get_token(user)

#         # Add custom claims
#         token['username'] = user.username
#         return token

class InstallerSignUpSerializer(serializers.Serializer):
    username = serializers.CharField(required=True,
                                    #  validators=[UniqueValidator(queryset=CustomUser.objects.all())]
                                     )
    password = serializers.CharField(required=True)
    email = serializers.EmailField(required=True,
                                #    validators=[UniqueValidator(queryset=CustomUser.objects.all())]
                                   )

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if username and password and email:
            if CustomUser.objects.filter(email=email).exists():
                raise serializers.ValidationError('E-mail already in use')
            elif CustomUser.objects.filter(username=username).exists():
                raise serializers.ValidationError(f'Username "{username}" already in use')

            return data
        else:
            raise serializers.ValidationError('Username, Email, and Password are all required')


class InstallerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installer
        fields = ['username', 'email', 'first_name', 'last_name']

class InstallerSignInSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            # Retrieve the user object using the provided username
            
            try:
                installer = Installer.objects.get(username=username)
            except Installer.DoesNotExist:
                raise serializers.ValidationError('Invalid credentials')

        
            if not check_password(password, installer.password):
                raise serializers.ValidationError('Invalid credentials')
            
            # If authentication successful, return the user
            data['installer'] = installer
            return data
        else:
            raise serializers.ValidationError('Username and password are required')
        


class InstallerAddUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True,
                                    #  validators=[UniqueValidator(queryset=CustomUser.objects.all())]
                                     )
    email = serializers.EmailField(required=True,
                                #    validators=[UniqueValidator(queryset=CustomUser.objects.all())]
                                   )
    first_name = serializers.CharField(required=True,
                                    #  validators=[UniqueValidator(queryset=CustomUser.objects.all())]
                                     )
    last_name = serializers.CharField(required=True,
                                    #  validators=[UniqueValidator(queryset=CustomUser.objects.all())]
                                     )

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')


        if username and email and first_name and last_name:
            if CustomUser.objects.filter(email=email).exists():
                raise serializers.ValidationError('E-mail already in use')
            elif CustomUser.objects.filter(username=username).exists():
                raise serializers.ValidationError(f'Username "{username}" already in use')
            return data
        else:
            raise serializers.ValidationError('Username, Email, and Password are all required')




class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['email', 'first_name', 'last_name','username']  # Include fields for serializer
    
    def create(self, validated_data):
        return UserProfile.objects.create(**validated_data)


class UserProfileSignInSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            # Retrieve the user object using the provided username
            
            try:
                user = UserProfile.objects.get(username=username)
            except UserProfile.DoesNotExist:
                raise serializers.ValidationError('Invalid credentials')

        
            if not check_password(password, user.password):
                raise serializers.ValidationError('Invalid credentials')
            
            # If authentication successful, return the user
            data['user'] = user
            return data
        else:
            raise serializers.ValidationError('Username and password are required')

