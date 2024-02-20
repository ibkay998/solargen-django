from rest_framework import serializers
from .models import Installer,UserProfile
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password,make_password
from django.contrib.auth import get_user_model
from .models import Installer, UserProfile, CustomUser
from rest_framework.validators import UniqueValidator
from rest_framework import status
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
loc = Nominatim(user_agent="Geopy Library")


def get_long_lat(country,state,city,street,houseNumber):
    if not state.lower().strip().endswith('State'):
        state += " state"
    addresses = [
        f"{houseNumber}, {street}, {city}, {state}, {country}",
        f"{street}, {city}, {state}, {country}",
        f"{city}, {state}, {country}",
        f"{state}, {country}",
    ]
    for address in addresses:
        getLoc = loc.geocode(address)
        # print(address,getLoc)
        if getLoc:
            return (getLoc.latitude, getLoc.longitude, getLoc.address)
    return (None, None, None)

class InstallerSignUpSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    other_names = serializers.CharField(required=False)

    location_houseNumber = serializers.IntegerField(required=True)
    location_street = serializers.CharField(required=True)
    location_city = serializers.CharField(required=True)
    location_state = serializers.CharField(required=True)
    location_country = serializers.CharField(required=True)

    company_name = serializers.CharField(required=True)
    contact_number = serializers.CharField(required=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        country = data.get('location_country')
        state = data.get('location_state')
        city = data.get('location_city')
        street = data.get('location_street')
        houseNumber = data.get('location_houseNumber')
        address_provided = f"{houseNumber}, {street}, {city}, {state}, {country}"

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        other_names = data.get('other_names')
        full_name = f"{first_name} {other_names} {last_name}"

        try:
            latitude, longitude, address_found = get_long_lat(country, state, city, street, houseNumber)
        except GeocoderTimedOut:
            raise serializers.ValidationError('Geocoding service timed out. Please ensure that your location is valid')
        
        data['latitude'] = latitude
        data['longitude'] = longitude
        data['address_found'] = address_found
        data['address_provided'] = address_provided
        
        data['full_name'] = full_name

        if (latitude is None) or (longitude is None):
            raise serializers.ValidationError('Cannot find the provided address!')

        if username and password and email:
            print("I entered here x3")
            if CustomUser.objects.filter(email=email).exists():
                print("I entered here x4")
                raise serializers.ValidationError('E-mail already in use')
            elif CustomUser.objects.filter(username=username).exists():
                print("I entered here x5")
                raise serializers.ValidationError(f'Username "{username}" already in use')
            return data
        else:
            raise serializers.ValidationError('Username, Email, and Password are all required')


class InstallerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installer
        fields = ['username', 'email', 'first_name', 'last_name','latitude','longitude']
        # fields = ['username','full_name','address_found','company_name','installed_assets','email','contact_number']

class InstallerProfileViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installer
        # fields = ['username', 'email', 'first_name', 'last_name','latitude','longitude']
        # fields = ['username','full_name','address_found','company_name','installed_assets','email','contact_number']
        fields = []


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

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if old_password and new_password:
            return data
        else:
            return serializers.ValidationError('Error!')
        

"""
USERS
"""


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

# class UserProfileChangePasswordSerializer(serializers.Serializer):
#     old_password = serializers.CharField(required=True)
#     new_password = serializers.CharField(required=True)

#     def validate(self, data):
#         old_password = data.get('old_password')
#         new_password = data.get('new_password')

#         if old_password and new_password:
#             return data
#         else:
#             return serializers.ValidationError('Error!')
        