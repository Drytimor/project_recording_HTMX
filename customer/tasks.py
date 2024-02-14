from django.core.cache import cache
from django.db.models import QuerySet

from allauth_app.settings import CACHE_KEY_ALL_OBJECT_FROM_DB, CACHE_KEY_USER_ASSIGNED_EVENTS
from organization.models import Organizations, Events

TIMEOUT_OBJECTS_ALL_FROM_CACHE = 60 * 5


def task_set_cache_assigned_user_events(assigned_user_events: dict, user_id: int):

    cache_key_user_assigned_events = CACHE_KEY_USER_ASSIGNED_EVENTS.format(user_id=user_id)

    cache.set(key=cache_key_user_assigned_events,
              value=assigned_user_events,
              timeout=TIMEOUT_OBJECTS_ALL_FROM_CACHE)


def task_set_cache_object(
        cache_key: str, value, timeout: int
):
    cache.set(key=cache_key,
              value=value,
              timeout=timeout)


def task_set_cache_organizations_all(organization: QuerySet['Organizations']):

    cache_key_organization_all = CACHE_KEY_ALL_OBJECT_FROM_DB.format(model='Organizations')
    cache.set(key=cache_key_organization_all,
              value=organization,
              timeout=TIMEOUT_OBJECTS_ALL_FROM_CACHE)


def task_set_cache_events_all(events: QuerySet['Events']):

    cache_key_events_all = CACHE_KEY_ALL_OBJECT_FROM_DB.format(model='Events')
    cache.set(key=cache_key_events_all,
              value=events,
              timeout=TIMEOUT_OBJECTS_ALL_FROM_CACHE)


def task_delete_assigned_user_events_from_cache(user_id: int):

    cache_key_user_assigned_events = CACHE_KEY_USER_ASSIGNED_EVENTS.format(user_id=user_id)
    cache.delete(cache_key_user_assigned_events)


def task_delete_records_all_from_cache():
    cache_key_records_all = CACHE_KEY_ALL_OBJECT_FROM_DB.format(model='Records')
    cache.delete(cache_key_records_all)

