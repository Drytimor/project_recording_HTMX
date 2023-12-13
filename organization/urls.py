from django.urls import path
from organization.views import organization_create, organization_profile, organization_update, organization_delete, \
    events_create, events_profile, events_update, events_delete, employee_create, employee_profile, employee_update, \
    employee_delete

urlpatterns = [

    path('create/', organization_create, name='organization_create'),
    path('profile/', organization_profile, name='organization_profile'),
    path('update/<int:pk>/', organization_update, name='organization_update'),
    path('delete/<int:pk>/', organization_delete, name='organization_delete'),

    path('create/', events_create, name='event_create'),
    path('profile/', events_profile, name='event_profile'),
    path('update/<int:pk>/', events_update, name='event_update'),
    path('delete/<int:pk>/', events_delete, name='event_delete'),

    path('create/', employee_create, name='employee_create'),
    path('profile/', employee_profile, name='employee_profile'),
    path('update/<int:pk>/', employee_update, name='employee_update'),
    path('delete/<int:pk>/', employee_delete, name='employee_delete'),

]
