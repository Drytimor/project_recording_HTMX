from django.urls import path, include

from customer.views import organizations_all, events_all

organizations_all_urlpatterns = [
    path('all/', organizations_all, name='org_all')
]

events_all_urlpatterns = [
    path('all/', events_all, name='events_all')
]

urlpatterns = [

    path('organizations/', include(organizations_all_urlpatterns)),
    path('events/', include(events_all_urlpatterns))
]