from django.db.models import QuerySet
from django.http import QueryDict
from django.forms import Form
from allauth_app.settings import AUTH_USER_MODEL
from customer.selectors import _create_filtered_object
from organization.models import Organizations, Employees, Events, Records
from django.db import transaction

from organization.selectors import (
    _get_user_organization_from_cache, _get_user_organization_from_db,
    _get_object_from_cache, _get_organization_employees_from_cache, _get_organization_employees_from_db,
    _get_organization_events_from_cache, _get_organization_events_from_db, _get_event_and_event_records_from_cache,
    _get_event_and_event_records_from_db, _get_user_from_user_object_in_cache, _get_employee_object, _get_event_profile,
    _get_event_object, _get_record_object, _get_organization_employees, OrganizationEventsFilter,
    OrganizationRecordsFilter)

from organization.tasks import (
    task_delete_object_from_cache, tasks_delete_queryset_from_cache, tasks_delete_model_objects_from_cache,
    tasks_delete_user_organization_objects_from_cache, tasks_set_user_organization_from_cache,
    tasks_set_user_object_from_cache, tasks_set_organization_employees_from_cache,
    tasks_set_organization_events_from_cache, tasks_set_event_records_from_cache)


TIMEOUT_CACHE_KEY_USER_OBJECTS = 60 ** 2 * 5


def _create_user_object_for_cache(user: 'AUTH_USER_MODEL') -> dict[str: 'AUTH_USER_MODEL', int]:

    user_object = {
        'user': user,
    }
    if user.organization_created:
        organization_id = Organizations.objects.filter(user=user).values('id').get().get('id')
        user_object['organization_id'] = organization_id

    return user_object


def _get_user_object(user_session_key: str, user: 'AUTH_USER_MODEL') -> dict:

    user_object = _get_object_from_cache(cache_key=user_session_key)
    if user_object is None:
        if user.pk:
            user_object = _create_user_object_for_cache(user=user)
            tasks_set_user_object_from_cache(
                user_object=user_object, session_key=user_session_key
            )
    return user_object


# Organization
@transaction.atomic
def create_organization_from_db(
        user: 'AUTH_USER_MODEL', session_key_user: str, cleaned_data: dict) -> 'Organizations':

    user_from_cache = _get_user_from_user_object_in_cache(session_key=session_key_user)

    if user_from_cache:
        user = user_from_cache
        task_delete_object_from_cache(cache_key=session_key_user)

    cleaned_data['user'] = user
    organization = Organizations.objects.create(**cleaned_data)
    user.organization_created = True
    user.save(update_fields=['organization_created'])

    return organization


@transaction.atomic
def update_organization_in_db(organization, cleaned_data: dict):

    organization_id = organization.pk
    organization_from_cache = _get_user_organization_from_cache(organization_id=organization_id)

    if organization_from_cache:
        tasks_delete_user_organization_objects_from_cache(organization_id=organization_id)

    Organizations.objects.filter(id=organization_id).update(**cleaned_data)


@transaction.atomic
def delete_organization_from_db(
        organization_id: int, session_key_user: str,
        user: 'AUTH_USER_MODEL'):

    organization = Organizations.objects.filter(id=organization_id).delete()
    user_from_cache = _get_user_from_user_object_in_cache(session_key=session_key_user)

    if user_from_cache:
        user = user_from_cache
        task_delete_object_from_cache(cache_key=session_key_user)

    user.organization_created = False
    user.save(update_fields=['organization_created'])

    tasks_delete_user_organization_objects_from_cache(organization_id=organization_id)

    return organization


def get_organization_object(organization_id: int) -> 'Organizations':
    organization = _get_user_organization_from_cache(organization_id=organization_id)

    if organization is None:
        organization = _get_user_organization_from_db(organization_id=organization_id)
        tasks_set_user_organization_from_cache(
            user_organization=organization, organization_id=organization_id)

    return organization


def get_user_organization(
        user_session_key: str, user: 'AUTH_USER_MODEL') -> 'Organizations' or None:

    user_object = _get_object_from_cache(
        cache_key=user_session_key, default=_create_user_object_for_cache(user=user))

    tasks_set_user_object_from_cache(
        user_object=user_object, session_key=user_session_key)

    organization_id = user_object.get('organization_id')

    if organization_id:
        organization = _get_user_organization_from_cache(organization_id=organization_id)

        if organization is None:
            organization = _get_user_organization_from_db(organization_id=organization_id)
            tasks_set_user_organization_from_cache(
                user_organization=organization, organization_id=organization_id)

        return organization


# Employees
@transaction.atomic
def create_employee_in_db(organization_id: int, cleaned_data: dict) -> 'Employees':

    employees = Employees.objects.create(**cleaned_data)
    tasks_delete_queryset_from_cache(
        queryset_name='organization_employees', object_id=organization_id)

    return employees


@transaction.atomic
def update_employee_in_db(employee: 'Employees', cleaned_data: dict,
                          organization_id: int):

    Employees.objects.filter(id=employee.pk).update(**cleaned_data)

    tasks_delete_queryset_from_cache(
        queryset_name='organization_employees', object_id=organization_id)


@transaction.atomic
def delete_employee_from_db(employee: 'Employees', organization_id: int):

    Employees.objects.filter(id=employee).delete()

    tasks_delete_queryset_from_cache(
        queryset_name='organization_employees', object_id=organization_id)


def get_employees_object(employee_id: int) -> 'Employees' or None:
    if employee_id:
        employee = _get_employee_object(employee_id=employee_id)
        return employee


def get_organization_employees_list(
        user_session_key: str, user: 'AUTH_USER_MODEL',
        data: QueryDict) -> tuple[QuerySet['Employees'], int] | tuple[None, None, None]:

    organization_employees, organization_id = None, None
    organization_id = data.get(key='organization')

    if organization_id is None:
        user_object = _get_user_object(
            user_session_key=user_session_key,
            user=user
        )
        organization_id = user_object.get('organization_id')

    if organization_id:
        organization_employees = _get_organization_employees_from_cache(organization_id=organization_id)

        if organization_employees is None:
            organization_employees = _get_organization_employees_from_db(organization_id=organization_id)
            tasks_set_organization_employees_from_cache(organization_employees=organization_employees, organization_id=organization_id)

    return organization_employees, organization_id


# Event
@transaction.atomic
def create_event_in_db(organization_id: int, cleaned_data: dict) -> 'Events':

    event_employees = cleaned_data.pop('employees')
    event = Events.objects.create(**cleaned_data)
    event.employees.set(event_employees)

    tasks_delete_queryset_from_cache(
        queryset_name='organization_events', object_id=organization_id)

    return event


@transaction.atomic
def update_event_in_db(event: 'Events', cleaned_data: dict,
                       organization_id: int) -> QuerySet['Employees']:

    event_employees = cleaned_data.pop('employees')
    Events.objects.filter(id=event.pk).update(**cleaned_data)
    event.employees.set(event_employees)

    tasks_delete_queryset_from_cache(
        queryset_name='organization_events', object_id=organization_id)

    return event_employees


@transaction.atomic
def delete_event_from_db(event_id: int, organization_id: int):
    Events.objects.filter(id=event_id).delete()

    tasks_delete_queryset_from_cache(
        queryset_name='organization_events', object_id=organization_id
    )
    tasks_delete_model_objects_from_cache(
        model_name='Events', object_id=event_id)


def get_event_profile(event_id: int) -> tuple['Events', 'Employees'] | None:
    if event_id:
        event, event_employees = _get_event_profile(event_id=event_id)
        return event, event_employees


def get_event_object(event_id: int) -> 'Events' or None:
    if event_id:
        event = _get_event_object(event_id=event_id)
        return event


def get_event_for_change(event_id: int, organization_id: int):

    event = _get_event_object(event_id=event_id)
    organization_employees = _get_organization_employees(organization_id=organization_id)

    return event, organization_employees


def get_organization_events(
        user_session_key: str, user: 'AUTH_USER_MODEL',
        data: QueryDict) -> tuple[QuerySet['Events'], 'Form', str, int] | tuple[None, None]:

    organization_events, organization_id, filter_form, params = None, None, None, None
    organization_id = data.get(key='organization')

    if organization_id is None:
        user_object = _get_user_object(
            user_session_key=user_session_key, user=user
        )
        organization_id = user_object.get('organization_id')

    if organization_id:
        organization_events = _get_organization_events_from_cache(organization_id=organization_id)
        if organization_events is None:
            organization_events = _get_organization_events_from_db(organization_id=organization_id)
            tasks_set_organization_events_from_cache(organization_events=organization_events, organization_id=organization_id)

        organization_events, filter_form, params = (
            _get_filtered_organization_events(
                queryset=organization_events,
                data=data)
        )

    return organization_events, filter_form, params, organization_id


def _get_filtered_organization_events(
        queryset: QuerySet, data: QueryDict) -> tuple[QuerySet['Events'], 'Form', str]:

    filter_class = OrganizationEventsFilter
    filtered_organization_events, filter_form = (
        _create_filtered_object(
            queryset=queryset, data=data,
            filter_class=filter_class)
    )
    data = data.copy()
    data.pop('organization', None)
    params = data.urlencode()

    return filtered_organization_events, filter_form, params


# Records
@transaction.atomic
def create_record_in_db(event_id: int, cleaned_data: dict) -> 'Records':

    record = Records.objects.create(**cleaned_data)

    tasks_delete_queryset_from_cache(
        queryset_name='event_records', object_id=event_id)

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


def get_record_object(record_id: int) -> 'Records' or None:
    if record_id:
        record = _get_record_object(record_id=record_id)
        return record


def get_event_and_event_records_for_organization_profile(
        event_id: int, data: QueryDict):

    event = _get_event_and_event_records_from_cache(event_id=event_id)

    if event is None:
        event = _get_event_and_event_records_from_db(event_id=event_id)
        tasks_set_event_records_from_cache(events=event, event_id=event_id)

    event_records = event.records.all()
    event_records, filter_form, params = _get_filtered_records(queryset=event_records, data=data)

    return event, event_records, filter_form, params


def _get_filtered_records(queryset: QuerySet, data: QueryDict) -> tuple[QuerySet['Records'], 'Form', str]:

    filter_class = OrganizationRecordsFilter
    filtered_records, filter_form = (
        _create_filtered_object(
            queryset=queryset, data=data,
            filter_class=filter_class)
    )
    params = data.urlencode()

    return filtered_records, filter_form, params
