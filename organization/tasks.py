from django.core.cache import cache
from allauth_app.settings import CACHE_KEY_QUERYSET, CACHE_KEY_MODEL_OBJECT_ID, CACHE_KEY_USER_ORGANIZATION_OBJECT
from organization.models import Organizations, Employees, Events
from django.db.models.query import QuerySet


TIMEOUT_CACHE_KEY_USER_OBJECTS = 60 ** 2 * 5
TIMEOUT_CACHE_KEY_USER_ORGANIZATION = 60 ** 2 * 5
TIMEOUT_CACHE_KEY_EVENT_RECORDS = 60 ** 2 * 5
TIMEOUT_CACHE_KEY_ORGANIZATION_EMPLOYEES = 60 * 5


def task_delete_object_from_cache(cache_key):
    cache.delete(cache_key)


def tasks_delete_queryset_from_cache(queryset_name: str, object_id: int):

    cache_key_queryset_name = CACHE_KEY_QUERYSET.format(
        queryset_name=queryset_name, object_id=object_id)

    cache.delete(cache_key_queryset_name)


def tasks_delete_model_objects_from_cache(model_name: str, object_id: int):

    cache_key_model_objects = CACHE_KEY_MODEL_OBJECT_ID.format(
        model_name=model_name, object_id=object_id)

    cache.delete(cache_key_model_objects)


def tasks_delete_user_organization_objects_from_cache(organization_id: int):

    cache_key_user_organization = CACHE_KEY_USER_ORGANIZATION_OBJECT.format(
        organization_id=organization_id)

    cache.delete(cache_key_user_organization)


def tasks_set_user_object_from_cache(user_object: dict, session_key: str):
    timeout = TIMEOUT_CACHE_KEY_USER_OBJECTS
    cache.set(
        key=session_key,
        value=user_object,
        timeout=timeout
    )


def tasks_set_user_organization_from_cache(user_organization: 'Organizations', organization_id: int):
    cache_key_user_organization = CACHE_KEY_USER_ORGANIZATION_OBJECT.format(
        organization_id=organization_id)

    timeout = TIMEOUT_CACHE_KEY_USER_ORGANIZATION
    cache.set(
        key=cache_key_user_organization,
        value=user_organization,
        timeout=timeout
    )


def tasks_set_organization_employees_from_cache(organization_employees: QuerySet['Employees'], organization_id: int):

    timeout = TIMEOUT_CACHE_KEY_ORGANIZATION_EMPLOYEES
    cache_key_organization_employees = CACHE_KEY_QUERYSET.format(
        queryset_name='organization_employees', object_id=organization_id)

    cache.set(key=cache_key_organization_employees,
              value=organization_employees,
              timeout=timeout)


def tasks_set_organization_events_from_cache(organization_events: QuerySet['Events'], organization_id: int):

    timeout = TIMEOUT_CACHE_KEY_ORGANIZATION_EMPLOYEES
    cache_key_organization_events = CACHE_KEY_QUERYSET.format(
        queryset_name='organization_events', object_id=organization_id)

    cache.set(key=cache_key_organization_events,
              value=organization_events,
              timeout=timeout)


def tasks_set_event_records_from_cache(events: QuerySet['Events'], event_id: int):

    timeout = TIMEOUT_CACHE_KEY_ORGANIZATION_EMPLOYEES
    cache_key_event_records = CACHE_KEY_QUERYSET.format(
        queryset_name='event_records', object_id=event_id)

    cache.set(key=cache_key_event_records,
              value=events,
              timeout=timeout)



