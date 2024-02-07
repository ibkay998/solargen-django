from django.contrib import admin
from .models import Installer, UserProfile,CustomUser

from django.contrib import admin

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    # Customize admin interface for installers
    pass

@admin.register(Installer)
class InstallerAdmin(admin.ModelAdmin):
    # Customize admin interface for installers
    pass

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # Customize admin interface for user profiles
    pass