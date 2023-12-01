from django.urls import path
from . import views


urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('nav_update/', views.UpdateNav.as_view(), name='nav_update'),
    path('clean_profile/', views.CleanProfile.as_view(), name='clean_profile'),
    path('auth_redirect/', views.AuthRedirect.as_view(), name='auth_redirect'),
    path('logout_redirect/', views.Logout.as_view(), name='logout_redirect'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('profile_htmx/<int:pk>/', views.ProfileHTMX.as_view(), name='profile_htmx'),
]