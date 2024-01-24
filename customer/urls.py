from django.urls import path, include, re_path

from customer.views import (organizations_all, events_all, organization_info, organization_events, event_info,
                            organization_employees, employee_info, event_records, record_sign_up, record_cancel,
                            records_user, record_user_delete, events_user, event_records_user, assigned_events,
                            delete_all_records_user)

organizations_urlpatterns = [

    path('all/<str:page>/', organizations_all, name='organizations_all'),
    path('info/<int:pk>', organization_info, name='organization_info'),
    path('events/', include([

        path('all/<int:pk>', organization_events, name='organization_events'),
        path('info/<int:org_pk>/<int:pk>/', event_info, name='event_info'),
        path('records/', include([

            path('<int:org_pk>/<int:event_pk>/', event_records, name='event_records'),
            path('sign_up/<int:pk>/', record_sign_up, name='record_sign_up'),
            path('cancel/<int:pk>/', record_cancel, name='record_cancel')

        ]))
    ])),

    path('employees/', include([

        path('all/<int:pk>', organization_employees, name='organization_employees'),
        path('info/<int:org_pk>/<int:pk>', employee_info, name='employee_info')

    ])),
]

events_urlpatterns = [

    path('all/<str:page>/', events_all, name='events_all'),
    path('assigned_events/<int:event_pk>', assigned_events, name='assigned_events'),
    path('profile/', include([

        path('list/', events_user, name='events_user'),
        path('delete/<int:user_pk>/<int:event_pk>/', delete_all_records_user, name='delete_all_records_user'),
        path('records/', include([

            path('user/<str:page>/<int:user_pk>/<int:event_pk>/', records_user, name='records_user'),
            path('event/<int:user_pk>/<int:event_pk>/', event_records_user, name='event_records_user'),
            path('delete/<int:pk>/<int:user_pk>/<int:event_pk>/', record_user_delete, name='record_user_delete')

        ])),

    ])),

]

urlpatterns = [

    path('organizations/', include(organizations_urlpatterns)),
    path('events/', include(events_urlpatterns)),

]
