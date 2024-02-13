from rest_framework import serializers
from .models import Installer,UserProfile
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password,make_password
from django.contrib.auth import get_user_model
from .models import Installer, UserProfile

# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

#     @classmethod
#     def get_token(cls, user):
#         token = super(MyTokenObtainPairSerializer, cls).get_token(user)

#         # Add custom claims
#         token['username'] = user.username
#         return token

class InstallerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installer
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = []

class InstallerSignInSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

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
        


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['email', 'first_name', 'last_name']  # Include fields for serializer
    
    def create(self, validated_data):
        return UserProfile.objects.create(**validated_data)


class UserProfileSignInSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

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
