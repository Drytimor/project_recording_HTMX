from django.contrib import admin
from django.urls import path, include

from core.views import signup, password_reset_from_key_done

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),



    path('accounts/', include('allauth.urls')),
    ]
