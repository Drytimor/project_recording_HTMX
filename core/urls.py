from django.urls import path, include
from .views import (home, auth_redirect, logout_redirect, profile, profile_update, profile_htmx,
                    profile_delete, signup, password_reset_from_key_done)

urlpatterns = [
    path('', home, name='home'),

    # переопределение SignupView django-allauth
    path('accounts/signup/', signup, name='account_signup'),
    # переопределение PasswordResetFromKeyDoneView django-allauth
    path('accounts/password/reset/key/done/', password_reset_from_key_done, name='account_reset_password_from_key_done'),

    path('auth_redirect/', auth_redirect, name='auth_redirect'),
    path('logout_redirect/', logout_redirect, name='logout_redirect'),

    path('profile/', profile, name='profile'),
    path('profile_update/', profile_update, name='profile_update'),
    path('profile_delete/', profile_delete, name='profile_delete'),
    path('profile_htmx/', profile_htmx, name='profile_htmx'),

    path('', include('organization.urls')),

]

