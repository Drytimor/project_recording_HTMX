from django.urls import path, include
from organization.views import (organization_create, organization_profile, organization_update, organization_delete,
                                events_create, events_list, events_update, events_delete, employee_create, employees_list,
                                employee_update, employee_delete)

organization_urlpatterns = [
    path('create/', organization_create, name='organization_create'),
    path('profile/', organization_profile, name='organization_profile'),
    path('update/<int:pk>', organization_update, name='organization_update'),
    path('delete/', organization_delete, name='organization_delete'),
]

event_urlpatterns = [
    path('create/<int:pk>', events_create, name='event_create'),
    path('profile/<int:pk>', events_list, name='events_list'),
    path('update/<int:pk>', events_update, name='event_update'),
    path('delete/<int:pk>', events_delete, name='event_delete'),
]

employee_urlpatterns = [
    path('create/<int:pk>', employee_create, name='employee_create'),
    path('profile/<int:pk>', employees_list, name='employees_list'),
    path('update/<int:pk>', employee_update, name='employee_update'),
    path('delete/<int:pk>', employee_delete, name='employee_delete'),
]

urlpatterns = [
    path('organization/', include(organization_urlpatterns)),
    path('event/', include(event_urlpatterns)),
    path('employees/', include(employee_urlpatterns)),
]