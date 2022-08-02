from django.contrib.auth import views as auth_views
from django.urls import path
from .views import *


urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomLogin.as_view(template_name='users/auth/login.html', ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('new-admin-registrations/', NewAdminRegistrationsListView.as_view(), name='new-admin-registrations'),
    path('new-admin-registrations/<int:user_pk>/approve', approve_admin_registration, name='aprove-admin-registration'),
    path('striked-users', StrikedUsersListView.as_view(), name='striked-users-list'),
    path('striked-users/<int:profile_pk>/remove-strike', remove_profile_strike, name='remove-profile-strike'),
]
