from django.db.models import Prefetch
from django.db.models.query import QuerySet
from django.http.request import QueryDict
from django.core.cache import cache
from allauth_app.settings import (
    CACHE_KEY_QUERYSET, CACHE_KEY_USER_ORGANIZATION_OBJECT, AUTH_USER_MODEL)
from customer.filters import create_filtered_object
from customer.tasks import task_set_cache_object
from organization.models import Organizations, Employees, Events, Records
from django.db import transaction
from django.forms import Form
from organization.tasks import (
    task_delete_object_from_cache, tasks_delete_queryset_from_cache, tasks_delete_model_objects_from_cache,
    tasks_delete_user_organization_objects_from_cache)


TIMEOUT_CACHE_KEY_USER_OBJECTS = 60 ** 2 * 5
TIMEOUT_CACHE_KEY_USER_ORGANIZATION = 60 ** 2 * 5
TIMEOUT_CACHE_KEY_EVENT_RECORDS = 60 ** 2 * 5


def _get_object_from_cache(cache_key: str):
    return cache.get(cache_key)


def _get_or_set_object_from_cache(
        cache_key: str, object_from_db, timeout: int):

    object_from_cache = cache.get(key=cache_key)

    if object_from_cache is None:

        task_set_cache_object(cache_key=cache_key,
                              value=object_from_db,
                              timeout=timeout)

        return object_from_db

    return object_from_cache


def _get_or_set_user_object_from_cache(
        session_key_for_cache: str, user: 'AUTH_USER_MODEL') -> dict | None:

    user_object_from_cache = cache.get(key=session_key_for_cache)
    timeout_cache = TIMEOUT_CACHE_KEY_USER_OBJECTS

    if user_object_from_cache is None:
        if user:
            user_object = {
                'user': user,
            }
            if user.organization_created:
                organization_id = Organizations.objects.filter(user=user).values('id').get().get('id')
                user_object['organization_id'] = organization_id

            task_set_cache_object(
                cache_key=session_key_for_cache,
                value=user_object,
                timeout=timeout_cache)

        else:
            return
    else:
        return user_object_from_cache

    return user_object


def _get_or_set_user_organization_from_cache(organization_id: int) -> 'Organizations':
    
    timeout_cache_key_user_organization = TIMEOUT_CACHE_KEY_USER_ORGANIZATION

    queryset_organization = (Organizations.objects.select_related('category')
                                                  .filter(id=organization_id))

    cache_key_user_organization = CACHE_KEY_USER_ORGANIZATION_OBJECT.format(
        organization_id=organization_id)

    organization_from_cache = cache.get(key=cache_key_user_organization)

    if organization_from_cache is None:

        organization_from_db = queryset_organization.get()

        task_set_cache_object(
            cache_key=cache_key_user_organization,
            value=organization_from_db,
            timeout=timeout_cache_key_user_organization)

        return organization_from_db

    return organization_from_cache


def get_user_id_from_cache_or_db(session_key_for_cache: str, user: 'AUTH_USER_MODEL'):
    return _get_or_set_user_object_from_cache(session_key_for_cache, user).get('user').pk


@transaction.atomic
def create_organization_from_db(
        user: 'AUTH_USER_MODEL', session_key_user: str, cleaned_data: dict) -> 'Organizations':

    user_from_cache = cache.get(key=session_key_user).get('user')

    if user_from_cache:
        user = user_from_cache
        task_delete_object_from_cache(cache_key=session_key_user)

    cleaned_data['user'] = user
    organization = Organizations.objects.create(**cleaned_data)
    user.organization_created = True
    user.save(update_fields=['organization_created'])

    return organization


def get_organization_object(organization_id: int) -> 'Organizations':

    organization = _get_or_set_user_organization_from_cache(organization_id=organization_id)

    return organization


def get_user_organization_from_profile(
        user_session_key: str, user: 'AUTH_USER_MODEL') -> 'Organizations' or None:

    user_object = _get_or_set_user_object_from_cache(
        session_key_for_cache=user_session_key, user=user)

    organization_id = user_object.get('organization_id')

    if organization_id:

        organization = _get_or_set_user_organization_from_cache(organization_id=organization_id)

        return organization


@transaction.atomic
def update_organization_in_db(organization, cleaned_data: dict):

    organization_id = organization.pk

    cache_key_user_organization = CACHE_KEY_USER_ORGANIZATION_OBJECT.format(
        organization_id=organization_id)

    organization_from_cache = cache.get(cache_key_user_organization)

    if organization_from_cache:

        tasks_delete_user_organization_objects_from_cache(organization_id=organization_id)

    Organizations.objects.filter(id=organization_id).update(**cleaned_data)


@transaction.atomic
def delete_organization_from_db(
        organization_id: int, session_key_user: str,
        user: 'AUTH_USER_MODEL'):

    organization = Organizations.objects.filter(id=organization_id).delete()

    user_from_cache = cache.get(key=session_key_user).get('user')

    if user_from_cache:
        user = user_from_cache
        task_delete_object_from_cache(cache_key=session_key_user)

    user.organization_created = False
    user.save(update_fields=['organization_created'])

    tasks_delete_user_organization_objects_from_cache(organization_id=organization_id)

    return organization


@transaction.atomic
def create_employee_in_db(organization_id: int, cleaned_data: dict) -> 'Employees':
    cleaned_data['organization_id'] = organization_id
    employees = Employees.objects.create(**cleaned_data)

    tasks_delete_queryset_from_cache(
        queryset_name='organization_employees', object_id=organization_id)

    return employees


def get_employees_object(employee_id: int) -> 'Employees' or None:
    if employee_id:
        employee = Employees.objects.get(id=employee_id)
        return employee


def get_organization_employees_list(
        session_key_user: str, user: 'AUTH_USER_MODEL',
        data: QueryDict) -> tuple[QuerySet['Employees'], int] | tuple[None, None]:

    organization_employees_list, organization_id = None, None

    organization_id = data.get(key='organization',
                               default=_get_or_set_user_object_from_cache(
                                   session_key_for_cache=session_key_user, user=user
                               ).get('organization_id'))

    if organization_id:

        organization_employees_list_from_db = Employees.objects.filter(organization=organization_id)

        cache_key_organization_employees = CACHE_KEY_QUERYSET.format(
            queryset_name='organization_employees', object_id=organization_id)

        organization_employees_list = _get_or_set_object_from_cache(
            cache_key=cache_key_organization_employees,
            object_from_db=organization_employees_list_from_db,
            timeout=60*5)

    return organization_employees_list, organization_id


@transaction.atomic
def update_employee_in_db(employee: 'Employees', cleaned_data: dict,
                          organization_id: int):

    Employees.objects.filter(id=employee.pk).update(**cleaned_data)

    tasks_delete_queryset_from_cache(
        queryset_name='organization_employees', object_id=organization_id)


def delete_employee_from_db(employee: 'Employees', organization_id: int):

    Employees.objects.filter(id=employee).delete()

    tasks_delete_queryset_from_cache(
        queryset_name='organization_employees', object_id=organization_id)


@transaction.atomic
def create_event_in_db(organization_id: int, cleaned_data: dict) -> 'Events':

    cleaned_data['organization_id'] = organization_id
    event_employees = cleaned_data.pop('employees')
    event = Events.objects.create(**cleaned_data)
    event.employees.set(event_employees)

    tasks_delete_queryset_from_cache(
        queryset_name='organization_events', object_id=organization_id)

    return event


def get_event_object(event_id: int) -> 'Events' or None:
    if event_id:
        event = Events.objects.get(id=event_id)
        return event


def get_organization_events(
        session_key_user: str, user: 'AUTH_USER_MODEL',
        data: QueryDict) -> tuple[QuerySet['Events'], int] | tuple[None, None]:

    organization_events, organization_id = None, None

    organization_id = data.get(key='organization',
                               default=_get_or_set_user_object_from_cache(
                                   session_key_for_cache=session_key_user, user=user
                               ).get('organization_id'))

    if organization_id:

        organization_events_from_db = Events.objects.filter(organization=organization_id)

        cache_key_organization_events = CACHE_KEY_QUERYSET.format(
            queryset_name='organization_events', object_id=organization_id)

        organization_events = _get_or_set_object_from_cache(
            cache_key=cache_key_organization_events,
            object_from_db=organization_events_from_db,
            timeout=60*5)

    return organization_events, organization_id


def get_filtered_organization_events(
        queryset: QuerySet, data: QueryDict,
        filter_class, filter_name: str = None) -> tuple[QuerySet['Events'], 'Form', str]:

    filtered_organization_events, filter_form = create_filtered_object(
        queryset=queryset, data=data,
        filter_class=filter_class, filter_name=filter_name)

    data = data.copy()
    data.pop('organization', None)

    return filtered_organization_events, filter_form, data.urlencode()


def get_event_profile_from_db(event_id: int) -> 'Events' or None:
    if event_id:
        event = (Events.objects.filter(id=event_id)
                               .prefetch_related(
                                Prefetch(lookup='employees',
                                         to_attr='employees_event'))
                               .get())
        return event


@transaction.atomic
def update_event_in_db(event,
                       cleaned_data: dict,
                       organization_id: int):

    event_employees = cleaned_data.pop('employees')
    Events.objects.filter(id=event.pk).update(**cleaned_data)
    event.employees.set(event_employees)

    tasks_delete_queryset_from_cache(
        queryset_name='organization_events', object_id=organization_id)


def delete_event_from_db(event_id: int, organization_id: int):
    Events.objects.filter(id=event_id).delete()

    tasks_delete_queryset_from_cache(
        queryset_name='organization_events', object_id=organization_id)

    tasks_delete_model_objects_from_cache(
        model_name='Events', object_id=event_id)


def get_filtered_event_records(event_records: QuerySet, data: QueryDict,
                               filter_class, filter_name: str = None) -> tuple[QuerySet['Records'], 'Form', str]:

    filtered_event_records, filter_form = create_filtered_object(
        queryset=event_records, data=data,
        filter_class=filter_class, filter_name=filter_name)

    params = data.urlencode()

    return filtered_event_records, filter_form, params


def get_event_and_all_records_from_db_for_organization(event_id: int) -> tuple[QuerySet['Events'], QuerySet['Records']]:

    cache_key_event_records = CACHE_KEY_QUERYSET.format(
        queryset_name='event_records', object_id=event_id)

    queryset_event_records = (Events.objects.filter(id=event_id)
                              .prefetch_related(
                              Prefetch(lookup='records'),
                              Prefetch(lookup='employees',
                                       to_attr='employees_event')))

    event_from_cache = cache.get(key=cache_key_event_records)

    if event_from_cache is None:
        event_from_db = queryset_event_records.get()

        task_set_cache_object(cache_key=cache_key_event_records,
                              value=event_from_db,
                              timeout=60*5)

        return event_from_db, event_from_db.records.all()

    return event_from_cache, event_from_cache.records.all()


def get_filtered_records(
        queryset: QuerySet, data: QueryDict,
        filter_class, filter_name: str = None) -> tuple[QuerySet['Records'], 'Form', str]:

    filtered_records, filter_form = create_filtered_object(
        queryset=queryset, data=data,
        filter_class=filter_class, filter_name=filter_name)

    params = data.urlencode()

    return filtered_records, filter_form, params


@transaction.atomic
def create_record_in_db(event_id: int, cleaned_data: dict) -> 'Records':

    cleaned_data['events_id'] = event_id
    record = Records.objects.create(**cleaned_data)

    tasks_delete_queryset_from_cache(
        queryset_name='event_records', object_id=event_id)

    return record


def get_record_object(record_id) -> 'Records' or None:
    if record_id:
        record = Records.objects.get(id=record_id)
        return record


@transaction.atomic
def update_record_in_db(
        record_id: int, event_id: int, cleaned_data: dict):

    Records.objects.filter(id=record_id).update(**cleaned_data)

    tasks_delete_queryset_from_cache(
        queryset_name='event_records', object_id=event_id)


def delete_record_from_db(record_id: int, event_id: int):

    Records.objects.filter(id=record_id).delete()

    tasks_delete_queryset_from_cache(
        queryset_name='event_records', object_id=event_id)



