from django.urls import path, include
from .views import (home, auth_redirect, logout_redirect, profile, profile_update,
                    profile_delete, signup, password_reset_from_key_done, form_update_profile)

urlpatterns = [
    path('', home, name='home'),

    # переопределение SignupView django-allauth
    path('accounts/signup/', signup, name='account_signup'),
    # переопределение PasswordResetFromKeyDoneView django-allauth
    path('accounts/password/reset/key/done/', password_reset_from_key_done, name='account_reset_password_from_key_done'),

    path('auth_redirect/', auth_redirect, name='auth_redirect'),
    path('logout_redirect/', logout_redirect, name='logout_redirect'),

    path('profile/', include([

        path('', profile, name='profile'),
        path('form/update/', form_update_profile, name='profile_form_update'),
        path('update/', profile_update, name='profile_update'),
        path('delete/', profile_delete, name='profile_delete'),

    ])),

    path('', include('organization.urls')),
    path('', include('customer.urls')),

]

