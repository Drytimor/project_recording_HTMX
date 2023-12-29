from django.urls import path, include
from organization.views import (organization_create, organization_profile, organization_update, organization_delete,
                                events_create, events_list, events_update, events_delete, employee_create,
                                employees_list, employee_update, employee_delete, event_profile, form_create_employee,
                                employee_profile, form_update_employee, form_update_event, form_create_event,
                                form_create_organization, form_update_organization, records_list, record_update,
                                record_delete, form_create_record, form_update_record, get_record, record_create,
                                get_employee, get_event, get_organization)

organization_urlpatterns = [

    path('form/', include([
        path('create/', form_create_organization, name='org_form_create'),
        path('update/<int:pk>', form_update_organization, name='org_form_update'),
    ])),

    path('create/', organization_create, name='organization_create'),
    path('profile/<int:pk>', organization_profile, name='organization_profile'),

    path('get/', include([
        path('<int:pk>/', get_organization, name='get_organization'),
        path('', get_organization, name='get_organization'),
    ])),

    path('update/<int:pk>', organization_update, name='organization_update'),
    path('delete/<int:pk>', organization_delete, name='organization_delete'),
]

event_urlpatterns = [

    path('form/', include([
        path('create/<int:pk>', form_create_event, name='event_form_create'),
        path('update/<int:org_pk>/<int:pk>', form_update_event, name='event_form_update'),
    ])),

    path('create/<int:pk>', events_create, name='event_create'),
    path('list/<int:pk>', events_list, name='events_list'),

    path('get/', include([
        path('<int:org_pk>/<int:pk>/', get_event, name='get_event'),
        path('', get_event, name='get_event'),
    ])),

    path('profile/<int:org_pk>/<int:pk>', event_profile, name='event_profile'),
    path('update/<int:org_pk>/<int:pk>', events_update, name='event_update'),
    path('delete/<int:pk>', events_delete, name='event_delete'),
]

employee_urlpatterns = [

    path('form/', include([
        path('create/<int:pk>', form_create_employee, name='employee_form_create'),
        path('update/<int:org_pk>/<int:pk>', form_update_employee, name='employee_form_update'),
    ])),

    path('create/<int:pk>', employee_create, name='employee_create'),
    path('list/<int:pk>', employees_list, name='employees_list'),

    path('get/', include([
        path('<int:org_pk>/<int:pk>/', get_employee, name='get_employee'),
        path('', get_employee, name='get_employee'),
    ])),

    path('profile/<int:org_pk>/<int:pk>', employee_profile, name='employee_profile'),
    path('update/<int:org_pk>/<int:pk>', employee_update, name='employee_update'),
    path('delete/<int:pk>', employee_delete, name='employee_delete'),
]

record_urlpatterns = [

    path('form/', include([
        path('create/<int:pk>', form_create_record, name='record_form_create'),
        path('update/<int:pk>', form_update_record, name='record_form_update'),
    ])),

    path('create/<int:pk>', record_create, name='record_create'),
    path('list/<int:org_pk>/<int:pk>', records_list, name='records_list'),

    path('get/', include([
        path('<int:pk>/', get_record, name='get_record'),
        path('', get_record, name='get_record'),
    ])),

    path('update/<int:pk>', record_update, name='record_update'),
    path('delete/<int:pk>', record_delete, name='record_delete'),
]

urlpatterns = [
    path('organization/', include(organization_urlpatterns)),
    path('event/', include(event_urlpatterns)),
    path('employee/', include(employee_urlpatterns)),
    path('record/', include(record_urlpatterns)),
]