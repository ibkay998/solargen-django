from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('installers/signup/', views.installer_signup, name='installer_signup'),
    path('installers/signin/', views.installer_signin, name='installer_signin'),
    path('installers/add_user/', views.add_user, name='add_user'),
    path('installers/change_password/', views.installer_change_password, name='installer_change_password'),
    path('installers/view_profile/', views.installer_view_profile, name='installer_view_profile'),

    path('users/signin/', views.user_signin, name='user_signin'),
    path('users/change_password/', views.user_change_password, name='user_change_password'),

]


router = DefaultRouter()
# router.register(r"user", views.UserProfileViewSet, basename="user")
urlpatterns += router.urls