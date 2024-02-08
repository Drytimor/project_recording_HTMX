from django.urls import path, include

from organization.views import (
    organization_create, organization_profile, organization_update, events_create, org_events_list, events_update, employee_create,
    org_employees_list, employee_update, event_profile, employee_profile,org_records_list, record_update,record_create, record_profile)


event_urlpatterns = [

    path('create/<int:org_pk>', events_create, name='event_create'),
    path('list/<str:page>', org_events_list, name='org_events_list'),

    path('profile/', include([
        path('<int:org_pk>/<int:event_pk>/', event_profile, name='event_profile'),
        path('', event_profile, name='event_profile'),
    ])),

    path('update/<int:org_pk>/<int:event_pk>', events_update, name='event_update'),
]

employee_urlpatterns = [

    path('create/<int:org_pk>', employee_create, name='employee_create'),
    path('list/<str:page>/', org_employees_list, name='org_employees_list'),

    path('profile/', include([
        path('<int:org_pk>/<int:emp_pk>', employee_profile, name='employee_profile'),
        path('', employee_profile, name='employee_profile'),
    ])),

    path('update/<int:org_pk>/<int:emp_pk>', employee_update, name='employee_update'),

]

record_urlpatterns = [

    path('create/<int:event_pk>', record_create, name='record_create'),
    path('list/<int:org_pk>/<int:event_pk>/<str:page>/', org_records_list, name='org_records_list'),

    path('profile/', include([
        path('<int:record_pk>/', record_profile, name='record_profile'),
        path('', record_profile, name='record_profile'),
    ])),

    path('update/<int:record_pk>', record_update, name='record_update'),
]

organization_urlpatterns = [

    path('event/', include(event_urlpatterns)),
    path('employee/', include(employee_urlpatterns)),
    path('record/', include(record_urlpatterns)),

    path('create/', organization_create, name='organization_create'),
    path('profile/', organization_profile, name='organization_profile'),
    path('update/<int:org_pk>', organization_update, name='organization_update'),
]

urlpatterns = [
    path('organization/', include(organization_urlpatterns)),
]
