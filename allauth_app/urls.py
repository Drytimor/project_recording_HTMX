from django.contrib import admin
from django.urls import path, include
from core import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/password/reset/key/done/",
        views.password_reset_from_key_done,
        name="account_reset_password_from_key_done",
    ),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
]
