from django.urls import path
from .views import (Home, UpdateNav, CleanProfile, AuthRedirect, Logout, Profile, ProfileUpdate, ProfileHTMX,
                    events_create, events_profile, events_update, events_delete, employee_create, employee_profile,
                    employee_update, employee_delete)

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('nav_update/', UpdateNav.as_view(), name='nav_update'),
    path('clean_profile/', CleanProfile.as_view(), name='clean_profile'),
    path('auth_redirect/', AuthRedirect.as_view(), name='auth_redirect'),
    path('logout_redirect/', Logout.as_view(), name='logout_redirect'),
    path('profile/', Profile.as_view(), name='profile'),
    path('profile_update/', ProfileUpdate.as_view(), name='profile_update'),
    path('profile_htmx/', ProfileHTMX.as_view(), name='profile_htmx'),

    path('event_create/', events_create, name='event_create'),
    path('event_profile/', events_profile, name='event_profile'),
    path('event_update/<int:pk>/', events_update, name='event_update'),
    path('event_delete/<int:pk>/', events_delete, name='event_delete'),

    path('employee_create/', employee_create, name='employee_create'),
    path('employee_profile/', employee_profile, name='employee_profile'),
    path('employee_update/<int:pk>/', employee_update, name='employee_update'),
    path('employee_delete/<int:pk>/', employee_delete, name='employee_delete'),
]