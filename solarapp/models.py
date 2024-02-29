from django.contrib.auth.models import AbstractUser
from django.db import models
from enum import Enum

#its going to be something like this

class CustomUser(AbstractUser):
    other_names = models.CharField(null=True, blank=True)
    full_name = models.CharField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)  # Geographical coordinates
    longitude = models.FloatField(null=True, blank=True)
    address_provided = models.CharField(null=True, blank=True)
    address_found = models.CharField(null=True, blank=True)
    contact_number = models.CharField(null=True, blank=True)
    

    
class Installer(CustomUser):
    installed_assets = models.IntegerField(default=0)
    installer_id = models.AutoField(primary_key=True)
    tariff = models.FloatField(null=True, blank=True)  # Rate per kilowatt-hour charged for energy
    company_name = models.CharField(null=True, blank=True)
    
    

class UserProfile(CustomUser):
    user_profile_id = models.AutoField(primary_key=True)
    tariff = models.FloatField(null=True, blank=True)  # Rate per kilowatt-hour charged for energy
    conventional_pricing = models.FloatField(null=True, blank=True)
    ai_dynamic_pricing = models.FloatField(null=True, blank=True)
    installer_profile = models.ForeignKey(Installer, on_delete=models.CASCADE, related_name='user_profiles_installer') ## TODO

class SolarSpecification(models.Model):
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='solar_specifications')
    potential_shading = models.BooleanField(default=False)
    solar_panel_type = models.CharField(max_length=100, blank=True)
    solar_size_watts = models.IntegerField(default=0)
    efficiency_ratings = models.IntegerField(default=0)
    total_number_of_panels = models.IntegerField(default=0)

    def __str__(self):
        return f"Solar Specification for {self.user_profile}"
    
class InverterSpecification(models.Model):
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='inverter_specifications')
    capacity_size = models.FloatField(default=0)  # Capacity/Size (kW/kVA)
    efficiency = models.FloatField(default=0)  # Efficiency (%)
    type = models.CharField(max_length=100, blank=True)  # Type
    voltage_input_range = models.FloatField(default=0)  # Voltage Input Range (V)
    mppt_channels = models.CharField(max_length=100, blank=True)  # MPPT Channels
    grid_type = models.CharField(max_length=100, blank=True)  # Grid-Tied/Off-Grid/Hybrid
    communication_features = models.CharField(max_length=200, blank=True)  # Communication Features
    protection_features = models.CharField(max_length=200, blank=True)  # Protection Features
    certifications = models.CharField(max_length=200, blank=True)  # Certifications

    def __str__(self):
        return f"Inverter Specification for {self.user_profile}"
    
class BatteryStorageSpecification(models.Model):
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='battery_storage_specifications')
    total_capacity_kwh = models.FloatField(default=0)  # Total Capacity (kWh)
    usable_capacity_kwh = models.FloatField(default=0)  # Usable Capacity (kWh)
    type_of_battery = models.CharField(max_length=100, blank=True)  # Type of Battery
    voltage_v = models.FloatField(default=0)  # Voltage (V)
    depth_of_discharge = models.FloatField(default=0)  # Depth of Discharge (DoD)
    cycle_life = models.IntegerField(default=0)  # Cycle Life
    charge_discharge_rate = models.FloatField(default=0)  # Charge/Discharge Rate
    efficiency = models.FloatField(default=0)  # Efficiency (%)
    management_system = models.CharField(max_length=200, blank=True)  # Management System
    warranty_and_lifespan = models.CharField(max_length=200, blank=True)  # Warranty and Lifespan

    def __str__(self):
        return f"Battery Storage Specification for {self.user_profile}"
    
class EnergyConsumptionData(models.Model):
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='energy_consumption_data')
    time = models.DateTimeField()  # Time
    load_watts = models.FloatField(default=0)  # Load (Watts)
    load_kw = models.FloatField(default=0)  # Load (kW)
    generation = models.FloatField(default=0)  # Generation (Watts/kW)
    tariff = models.FloatField(default=0)  # Tariff (Naira/kWh)
    charge = models.FloatField(default=0)  # Charge (Naira)
    dynamic_tariff = models.CharField(max_length=200, blank=True)  # Dynamic Tariff (Naira/kWh)
    dynamic_charge = models.FloatField(default=0)  # Dynamic Charge (Naira)
    wasted_energy = models.FloatField(default=0)  # Wasted Energy (Watts/kW)

    def __str__(self):
        return f"Energy Consumption Data for {self.user_profile} at {self.time}"

# # Creating an instance of installer_0
# installer_0, created = Installer.objects.get_or_create(username='installer_0')

# # Signal to handle deletion of installers
# @receiver(pre_delete, sender=Installer)
# def pre_delete_installer(sender, instance, **kwargs):
#     if instance != installer_0:
#         # Assign users within the deleted installer to installer_0
#         UserProfile.objects.filter(installer=instance).update(installer=installer_0)