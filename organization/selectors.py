from django.core.cache import cache
from django.db.models import Prefetch, QuerySet
from allauth_app.settings import CACHE_KEY_USER_ORGANIZATION_OBJECT, CACHE_KEY_QUERYSET
from customer.selectors import EventsFilter, RecordsListUserFilter

from organization.models import Organizations, Employees, Events, Records


def _get_object_from_cache(cache_key: str, default=None):
    return cache.get(cache_key, default=default)


def _get_user_from_user_object_in_cache(session_key: str):
    user_object = cache.get(session_key)
    if user_object:
        return user_object.get('user')


# Organization
def _get_user_organization_from_cache(organization_id: int) -> 'Organizations':

    cache_key_user_organization = CACHE_KEY_USER_ORGANIZATION_OBJECT.format(
        organization_id=organization_id)

    user_organization_from_cache = _get_object_from_cache(cache_key=cache_key_user_organization)
    return user_organization_from_cache


def _get_user_organization_from_db(organization_id: int) -> 'Organizations':

    user_organization = (
        Organizations.objects.select_related('category')
                             .filter(id=organization_id)
                             .get()
    )
    return user_organization


def _get_organization_employees(organization_id: int) -> QuerySet['Employees']:

    organization_employees = Employees.objects.filter(organization=organization_id)
    return organization_employees


# Employees
def _get_employee_object(employee_id: int):

    employee = Employees.objects.get(id=employee_id)
    return employee


def _get_organization_employees_from_cache(organization_id: int):

    cache_key_organization_employees = CACHE_KEY_QUERYSET.format(
        queryset_name='organization_employees', object_id=organization_id)

    organization_employees = _get_object_from_cache(cache_key=cache_key_organization_employees)
    return organization_employees


def _get_organization_employees_from_db(organization_id: int):

    organization_employees_from_db = Employees.objects.filter(organization=organization_id)
    return organization_employees_from_db


# Event
class OrganizationEventsFilter(EventsFilter):

    category = ...

    class Meta:
        fields = [
            'tariff'
        ]


def _get_event_object(event_id: int):
    event = Events.objects.get(id=event_id)
    return event


def _get_event_profile(event_id: int):

    event = (Events.objects.filter(id=event_id)
                           .prefetch_related(
                            Prefetch(lookup='employees',
                                     to_attr='event_employees'
                                     ))
                           .get())

    event_employees = event.event_employees

    return event, event_employees


def _get_event_update(event_id: int, organization_id: int):

    event = _get_event_object(event_id=event_id)
    event_employees = Employees.objects.filter(organization=organization_id)

    return event, event_employees


def _get_organization_events_from_cache(organization_id: int):

    cache_key_organization_events = CACHE_KEY_QUERYSET.format(
        queryset_name='organization_events', object_id=organization_id)

    organization_events_from_cache = _get_object_from_cache(cache_key=cache_key_organization_events)
    return organization_events_from_cache


def _get_organization_events_from_db(organization_id: int):

    organization_events_from_db = Events.objects.filter(organization=organization_id)
    return organization_events_from_db


# Record
class OrganizationRecordsFilter(RecordsListUserFilter):
    ...


def _get_record_object(record_id: int) -> 'Records':

    record = Records.objects.get(id=record_id)
    return record


def _get_event_and_event_records_from_cache(event_id: int):

    cache_key_event_records = CACHE_KEY_QUERYSET.format(
        queryset_name='event_records', object_id=event_id)

    event = _get_object_from_cache(
        cache_key=cache_key_event_records
    )
    return event


def _get_event_and_event_records_from_db(event_id: int):

    event = (Events.objects.filter(id=event_id)
                           .prefetch_related(
                               Prefetch(lookup='records'),
                               Prefetch(lookup='employees',
                                        to_attr='employees_event')
                           ).get())

    return event




