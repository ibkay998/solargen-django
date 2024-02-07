from django.contrib.auth.models import AbstractUser
from django.db import models
from enum import Enum

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('user', 'User'),
        ('installer', 'Installer'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    
class Installer(CustomUser):
    class Meta:
        proxy = True

class UserProfile(CustomUser):
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