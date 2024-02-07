from django.contrib.auth.models import AbstractUser
from django.db import models
from enum import Enum

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('user', 'User'),
        ('installer', 'Installer'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    REQUIRED_FIELDS = ['email','password']

    
class Installer(CustomUser):
    # installed_assets = models.IntegerField(default=0)  # Number of installed assets
    # latitude = models.FloatField(null=True, blank=True)  # Geographical coordinates
    # longitude = models.FloatField(null=True, blank=True)
    # temperature = models.FloatField(null=True, blank=True)  # Ambient temperature
    # humidity = models.FloatField(null=True, blank=True)  # Humidity levels
    # precipitation = models.FloatField(null=True, blank=True)  # Precipitation
    # potential_shading = models.BooleanField(default=False)  # Potential shading
    # solar_size_watts = models.IntegerField(null=True, blank=True)  # Total wattage capacity of solar installation
    # efficiency_ratings = models.IntegerField(null=True, blank=True)  # Efficiency ratings of solar panels
    # total_number_of_panels = models.IntegerField(null=True, blank=True)  # Total count of solar panels
    class Meta:
        proxy = True

class UserProfile(CustomUser):
    # installer = models.ForeignKey(Installer, on_delete=models.CASCADE)
    # time = models.DateTimeField()  # Specific hour of the day for energy measurements
    # load_watts = models.FloatField()  # Measured energy consumption in watts
    # load_kw = models.FloatField()  # Measured energy consumption in kilowatts
    # generation = models.FloatField()  # Measured energy generation by the solar asset
    # tariff = models.FloatField()  # Rate per kilowatt-hour charged for energy
    # charge = models.FloatField()  # Total cost of energy consumed (load x tariff)
    # dynamic_charge = models.FloatField()  # Cost of energy calculated using the dynamic tariff
    # wasted_energy = models.FloatField()  # Differe
    class Meta:
        proxy = True

# # Creating an instance of installer_0
# installer_0, created = Installer.objects.get_or_create(username='installer_0')

# # Signal to handle deletion of installers
# @receiver(pre_delete, sender=Installer)
# def pre_delete_installer(sender, instance, **kwargs):
#     if instance != installer_0:
#         # Assign users within the deleted installer to installer_0
#         UserProfile.objects.filter(installer=instance).update(installer=installer_0)