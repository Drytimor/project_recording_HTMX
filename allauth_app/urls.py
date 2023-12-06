from django.contrib import admin
from django.urls import path, include
from core.views import signup, password_reset_from_key_done

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/password/reset/key/done/',  # переопределение allauth.account.views
         password_reset_from_key_done,  # PasswordResetFromKeyDoneView
         name='account_reset_password_from_key_done'),
    path('accounts/signup/', signup,  # переопределение allauth.account.views
         name='account_signup'),  # SignupView
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
    ]
