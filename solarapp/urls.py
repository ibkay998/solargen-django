from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

urlpatterns = [
    # path('api/signup/', views.signup, name='signup'),
    # path('api/login/', views.login, name='login'),
    # path('api/users/', views.user_list, name='user-list'),
    path('installers/signup/', views.installer_signup, name='installer_signup'),
    path('installers/signin/', views.installer_signin, name='installer_signin'),
    path('installers/<int:installer_id>/add_user/', views.add_user, name='add_user'),
    path('installers/<int:installer_id>/users/<int:user_id>/user_initial_password/', views.get_user_initial_password, name='get_initial_password'),
    path('users/signin/', views.user_signin, name='user_signin'),
    path('users/change_password/', views.user_change_password, name='user_change_password'),

]


router = DefaultRouter()
router.register(r"user", views.UserProfileViewSet, basename="user")
urlpatterns += router.urls