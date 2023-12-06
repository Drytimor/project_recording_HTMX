from django.urls import path
from .views import Home, UpdateNav, CleanProfile, AuthRedirect, Logout, Profile, ProfileUpdate, ProfileHTMX, \
    organization_create, organization_profile, organization_update, organization_delete

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('nav_update/', UpdateNav.as_view(), name='nav_update'),
    path('clean_profile/', CleanProfile.as_view(), name='clean_profile'),
    path('auth_redirect/', AuthRedirect.as_view(), name='auth_redirect'),
    path('logout_redirect/', Logout.as_view(), name='logout_redirect'),
    path('profile/', Profile.as_view(), name='profile'),
    path('profile_update/', ProfileUpdate.as_view(), name='profile_update'),
    path('profile_htmx/', ProfileHTMX.as_view(), name='profile_htmx'),
    path('organization_create/', organization_create, name='organization_create'),
    path('organization_profile/', organization_profile, name='organization_profile'),
    path('organization_update/', organization_update, name='organization_update'),
    path('organization_delete/', organization_delete, name='organization_delete'),
]