from django.urls import path, include
from organization.views import (
    organization_create, organization_profile, organization_update, organization_delete,
    events_create, org_events_list, events_update, events_delete, employee_create,
    org_employees_list, employee_update, employee_delete, event_profile, form_create_employee,
    employee_profile, form_update_employee, form_update_event, form_create_event,
    form_create_organization, form_update_organization, org_records_list, record_update,
    record_delete, form_create_record, form_update_record, record_create, record_profile)


event_urlpatterns = [

    path('form/', include([
        path('create/<int:org_pk>', form_create_event, name='event_form_create'),
        path('update/<int:org_pk>/<int:event_pk>', form_update_event, name='event_form_update'),
    ])),

    path('create/<int:org_pk>', events_create, name='event_create'),
    path('list/<str:page>', org_events_list, name='org_events_list'),

    path('profile/', include([
        path('<int:org_pk>/<int:event_pk>/', event_profile, name='event_profile'),
        path('', event_profile, name='event_profile'),
    ])),

    path('update/<int:org_pk>/<int:event_pk>', events_update, name='event_update'),
    path('delete/<int:org_pk>/<int:event_pk>', events_delete, name='event_delete'),
]

employee_urlpatterns = [

    path('form/', include([
        path('create/<int:org_pk>', form_create_employee, name='employee_form_create'),
        path('update/<int:org_pk>/<int:emp_pk>', form_update_employee, name='employee_form_update'),
    ])),

    path('create/<int:org_pk>', employee_create, name='employee_create'),
    path('list/<str:page>/', org_employees_list, name='org_employees_list'),

    path('profile/', include([
        path('<int:org_pk>/<int:emp_pk>', employee_profile, name='employee_profile'),
        path('', employee_profile, name='employee_profile'),
    ])),

    path('update/<int:org_pk>/<int:emp_pk>', employee_update, name='employee_update'),
    path('delete/<int:org_pk>/<int:emp_pk>', employee_delete, name='employee_delete'),

]

record_urlpatterns = [

    path('form/', include([
        path('create/<int:event_pk>', form_create_record, name='record_form_create'),
        path('update/<int:record_pk>', form_update_record, name='record_form_update'),
    ])),

    path('create/<int:event_pk>', record_create, name='record_create'),
    path('list/<int:org_pk>/<int:event_pk>/<str:page>/', org_records_list, name='org_records_list'),

    path('get/', include([
        path('<int:record_pk>/', record_profile, name='record_profile'),
        path('', record_profile, name='record_profile'),
    ])),

    path('update/<int:record_pk>', record_update, name='record_update'),
    path('delete/<int:record_pk>', record_delete, name='record_delete'),
]

organization_urlpatterns = [

    path('event/', include(event_urlpatterns)),
    path('employee/', include(employee_urlpatterns)),
    path('record/', include(record_urlpatterns)),

    path('form/', include([
        path('create/', form_create_organization, name='org_form_create'),
        path('update/<int:org_pk>', form_update_organization, name='org_form_update'),
    ])),

    path('create/', organization_create, name='organization_create'),
    path('profile/', organization_profile, name='organization_profile'),

    path('update/<int:org_pk>', organization_update, name='organization_update'),
    path('delete/<int:org_pk>', organization_delete, name='organization_delete'),
]

urlpatterns = [
    path('organization/', include(organization_urlpatterns)),
]
