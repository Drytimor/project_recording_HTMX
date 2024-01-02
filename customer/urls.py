from django.urls import path, include

from customer.views import (organizations_all, events_all, organization_info, organization_events, event_info,
                            organization_employees, employee_info, event_records, record_sign_up, records_list)

organizations_urlpatterns = [
    path('all/', organizations_all, name='organization_all'),
    path('info/<int:pk>', organization_info, name='organization_info'),

    path('events/', include([
        path('all/<int:pk>', organization_events, name='organization_events'),

        path('info/<int:org_pk>/<int:pk>/', event_info, name='event_info'),

        path('records/', include([
            path('<int:org_pk>/<int:pk>/', event_records, name='event_records'),
            path('sign_up/<int:pk>/', record_sign_up, name='record_sign_up')
        ]))
    ])),

    path('employees/', include([
        path('all/<int:pk>', organization_employees, name='organization_employees'),
        path('info/<int:org_pk>/<int:pk>', employee_info, name='employee_info')
    ])),
]

events_urlpatterns = [
    path('all/', events_all, name='events_all'),

    path('card/', include([
        # path('<int:pk>/', event_card, name='event_card'),
        path('records/<int:pk>/', records_list, name='records_list')
    ])),
]

urlpatterns = [

    path('organizations/', include(organizations_urlpatterns)),
    path('events/', include(events_urlpatterns))
]