from rest_framework import serializers
from .models import Installer,UserProfile
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password,make_password
from django.contrib.auth import get_user_model
from .models import Installer, UserProfile, CustomUser,SolarSpecification, InverterSpecification, BatteryStorageSpecification,EnergyConsumptionData
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




class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    contact = serializers.CharField(required=True)
    name_of_asset = serializers.CharField(required=True)
    number_of_installed_assets = serializers.IntegerField(required=True)
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    solar_size_watts = serializers.IntegerField(required=True)
    efficiency_ratings = serializers.IntegerField(required=True)
    total_number_of_panels = serializers.IntegerField(required=True)
    capacity_size = serializers.FloatField(required=True)
    efficiency = serializers.FloatField(required=True)
    voltage_input_range = serializers.FloatField(required=True)
    total_capacity_kwh = serializers.FloatField(required=True)
    voltage_v = serializers.FloatField(required=True)
    conventional_pricing = serializers.FloatField(required=True)
    ai_dynamic_pricing = serializers.FloatField(required=True)

    class Meta:
        model = UserProfile
        fields = ['user_email', 'phone', 'name_of_asset', 'number_of_installed_assets',
                  'latitude', 'longitude', 'solar_size_watts', 'efficiency_ratings',
                  'total_number_of_panels', 'capacity_size', 'efficiency', 'voltage_input_range',
                  'total_capacity_kwh', 'voltage_v', 'conventional_pricing', 'ai_dynamic_pricing']

    def create(self, validated_data):
        # Extract solar specification data
        solar_spec_data = validated_data.pop('solar_specification', None)
        # Extract inverter specification data
        inverter_spec_data = validated_data.pop('inverter_specification', None)
        # Extract battery storage specification data
        battery_spec_data = validated_data.pop('battery_storage_specification', None)
        
        # Create UserProfile instance
        user_profile = UserProfile.objects.create(**validated_data)
        
        # Create related models instances
        if solar_spec_data:
            SolarSpecification.objects.create(user_profile=user_profile, **solar_spec_data)
        if inverter_spec_data:
            InverterSpecification.objects.create(user_profile=user_profile, **inverter_spec_data)
        if battery_spec_data:
            BatteryStorageSpecification.objects.create(user_profile=user_profile, **battery_spec_data)
        
        return user_profile

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
        full_name = f"{first_name} {other_names} {last_name}" if other_names else f"{first_name} {last_name}"

        try:
            latitude, longitude, address_found = get_long_lat(country, state, city, street, houseNumber)
            data['latitude'] = latitude
            data['longitude'] = longitude
            data['address_found'] = address_found
        except GeocoderTimedOut:
            data['latitude'] = 0
            data['longitude'] = 0
            data['address_found'] = ''
        
        
        data['address_provided'] = address_provided
        
        data['full_name'] = full_name

        # if (latitude is None) or (longitude is None):
        #     raise serializers.ValidationError('Cannot find the provided address!')

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
        fields = ['username', 'email', 'first_name','last_name','latitude','longitude']
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
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    other_names = serializers.CharField(required=False)
    location_houseNumber = serializers.IntegerField(required=True)
    location_street = serializers.CharField(required=True)
    location_city = serializers.CharField(required=True)
    location_state = serializers.CharField(required=True)
    location_country = serializers.CharField(required=True)
    contact = serializers.CharField(required=True)
    solar_size_watts = serializers.IntegerField(required=True)
    efficiency_ratings = serializers.IntegerField(required=True)
    total_number_of_panels = serializers.IntegerField(required=True)
    capacity_size = serializers.FloatField(required=True)
    efficiency = serializers.FloatField(required=True)
    voltage_input_range = serializers.FloatField(required=True)
    total_capacity_kwh = serializers.FloatField(required=True)
    voltage_v = serializers.FloatField(required=True)
    conventional_pricing = serializers.FloatField(required=True)
    ai_dynamic_pricing = serializers.FloatField(required=True)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        country = data.get('location_country')
        state = data.get('location_state')
        city = data.get('location_city')
        other_names = data.get('other_names')
        street = data.get('location_street')
        houseNumber = data.get('location_houseNumber')
        address_provided = f"{houseNumber}, {street}, {city}, {state}, {country}"
        
        full_name = f"{first_name} {other_names} {last_name}" if other_names else f"{first_name} {last_name}"
        

        try:
            latitude, longitude, address_found = get_long_lat(country, state, city, street, houseNumber)
            data['latitude'] = latitude
            data['longitude'] = longitude
            data['address_found'] = address_found
        except GeocoderTimedOut:
            data['latitude'] = 0
            data['longitude'] = 0
            data['address_found'] = ''

        data['address_provided'] = address_provided
        data['full_name'] = full_name

        if username and email and first_name and last_name:
            if CustomUser.objects.filter(email=email).exists():
                raise serializers.ValidationError('E-mail already in use')
            elif CustomUser.objects.filter(username=username).exists():
                raise serializers.ValidationError(f'Username "{username}" already in use')
            return data
        else:
            raise serializers.ValidationError('Username, Email, First Name, Last Name, and Contact are all required')

    def create(self, validated_data):
        # Extract solar specification data
        solar_spec_data = {
            'solar_size_watts': validated_data.pop('solar_size_watts'),
            'efficiency_ratings': validated_data.pop('efficiency_ratings'),
            'total_number_of_panels': validated_data.pop('total_number_of_panels')
        }

        # Extract inverter specification data
        inverter_spec_data = {
            'capacity_size': validated_data.pop('capacity_size'),
            'efficiency': validated_data.pop('efficiency'),
            'voltage_input_range': validated_data.pop('voltage_input_range')
        }

        # Extract battery storage specification data
        battery_spec_data = {
            'total_capacity_kwh': validated_data.pop('total_capacity_kwh'),
            'voltage_v': validated_data.pop('voltage_v')
        }

        # Create CustomUser instance
        
        installer = self.context.get('installer')
        hashed_password = make_password('password123')
        validated_data['password'] = hashed_password
        
    
        # Create CustomUser instance with the installer_profile
        validated_data.pop('location_houseNumber', None)
        validated_data.pop('location_street', None)
        validated_data.pop('location_city', None)
        validated_data.pop('location_state', None)
        validated_data.pop('location_country', None)
        validated_data["contact_number"] = validated_data["contact"]
        validated_data.pop('contact', None)

        

        user_profile = UserProfile.objects.create(installer_profile=installer, **validated_data)

        

        # Create related models instances
        SolarSpecification.objects.create(user_profile=user_profile, **solar_spec_data)
        InverterSpecification.objects.create(user_profile=user_profile, **inverter_spec_data)
        BatteryStorageSpecification.objects.create(user_profile=user_profile, **battery_spec_data)
    

        # Increment the installed_assets
        installer.installed_assets += 1

        # Save the installer
        installer.save()
        
        
        return user_profile
    

class SolarSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolarSpecification
        fields = '__all__'

class InverterSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InverterSpecification
        fields = '__all__'

class BatteryStorageSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatteryStorageSpecification
        fields = '__all__'

class EnergyConsumptionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyConsumptionData
        fields = '__all__'

class UserProfileWithSpecificationsSerializer(serializers.ModelSerializer):
    # solar_specification = SolarSpecificationSerializer()
    # inverter_specification = InverterSpecificationSerializer()
    # battery_storage_specification = BatteryStorageSpecificationSerializer()

    class Meta:
        model = UserProfile
        fields = '__all__'
        

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
        