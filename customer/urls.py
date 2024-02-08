from django.urls import path, include, re_path

from customer.views import (
    organizations_all, events_all, organization_info, organization_events, event_info,
    organization_employees, employee_info, event_records,
    user_records_in_event, events_user, assigned_events, records_event_for_user,
)

organizations_urlpatterns = [

    path('all/<str:page>/', organizations_all, name='organizations_all'),
    path('info/<int:org_pk>', organization_info, name='organization_info'),
    path('events/', include([

        path('all/<int:org_pk>/<str:page>/', organization_events, name='organization_events'),
        path('info/<int:org_pk>/<int:event_pk>/', event_info, name='event_info'),
        path('records/', include([

            path('<int:org_pk>/<int:event_pk>/<str:page>/', event_records, name='event_records'),
            path('', event_records, name='event_records'),

        ]))
    ])),

    path('employees/', include([

        path('all/<int:org_pk>/<str:page>/', organization_employees, name='organization_employees'),
        path('info/<int:org_pk>/<int:emp_pk>/', employee_info, name='employee_info')

    ])),
]

events_urlpatterns = [

    path('all/<str:page>/', events_all, name='events_all'),
    path('assigned_events/<int:event_pk>', assigned_events, name='assigned_events'),
    path('profile/', include([

        path('list/<str:page>/', events_user, name='events_user'),
        path('delete/<int:user_pk>/<int:event_pk>/', events_user, name='delete_all_records_user'),
        path('records/', include([

            path('user/profile/', include([
                path('records/<str:page>/<int:user_pk>/<int:event_pk>/', user_records_in_event, name='user_records_in_event'),
                path('delete/<int:record_pk>/<int:user_pk>/', user_records_in_event, name='delete_user_record'),
                path('event_records/<str:page>/<int:user_pk>/<int:event_pk>/', records_event_for_user, name='records_event_for_user'),
                path('event_records/cansel/', records_event_for_user, name='cancel_user_record'),
            ])),


        ])),

    ])),

]

urlpatterns = [

    path('organizations/', include(organizations_urlpatterns)),
    path('events/', include(events_urlpatterns)),

]
