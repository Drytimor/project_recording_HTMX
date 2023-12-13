from django.urls import path, include
from .views import (Home, UpdateNav, CleanProfile, AuthRedirect, Logout, Profile, ProfileUpdate, ProfileHTMX,
                    profile_delete, signup, password_reset_from_key_done)

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('nav_update/', UpdateNav.as_view(), name='nav_update'),
    path('clean_profile/', CleanProfile.as_view(), name='clean_profile'),
    path('auth_redirect/', AuthRedirect.as_view(), name='auth_redirect'),
    path('logout_redirect/', Logout.as_view(), name='logout_redirect'),

    path('accounts/signup/', signup,  # переопределение allauth.account.views
         name='account_signup'),  # SignupView

    path('accounts/password/reset/key/done/',  # переопределение allauth.account.views
         password_reset_from_key_done,  # PasswordResetFromKeyDoneView
         name='account_reset_password_from_key_done'),

    path('profile/', Profile.as_view(), name='profile'),
    path('profile_update/<int:pk>/', ProfileUpdate.as_view(), name='profile_update'),
    path('profile_delete/<int:pk>', profile_delete, name='profile_delete'),
    path('profile_htmx/', ProfileHTMX.as_view(), name='profile_htmx'),

    path('', include('organization.urls')),

]