from django.db.models import F
from django.db import transaction

from allauth_app.settings import (
    CACHE_KEY_MODEL_OBJECT_ID, CACHE_KEY_FILTER_NAME, AUTH_USER_MODEL)

from customer.models import StatusRecordingChoices, Recordings, AssignedEvents

from customer.selectors import (
    _get_organizations_all_from_cache, _get_organizations_all_from_db, OrganizationFilter,
    EventsFilter, EventsListUserFilter, _create_filtered_object, QuerySet, _get_organization_events_from_db,
    QueryDict, _get_organization_object_from_db, _get_events_all_from_cache, _get_events_all_from_db,
    _get_assigned_user_events_from_cache, _get_assigned_user_events_from_db,
    _get_event_card_from_db, EventRecordsListFilter,
    _get_user_records_in_event_from_db, UserRecordsInEventFilter, _get_event_records,
    _get_event_records_with_registered_user_field, _get_user_events_with_assigned_field_for_profile
)

from customer.tasks import (
    task_set_cache_organizations_all, cache, task_set_cache_events_all,
    task_delete_assigned_user_events_from_cache, task_set_cache_assigned_user_events,
    task_delete_records_all_from_cache)

from organization.models import Organizations, Events, Records
from organization.selectors import OrganizationEventsFilter, _get_organization_employees, _get_event_profile
from organization.services import _get_user_object
from django.forms import Form


# CRUD Organization
def get_organizations_all(data: QueryDict) -> tuple[QuerySet['Organizations'], 'Form', str]:

    organizations = _get_organizations_all_from_cache()
    if organizations is None:
        organizations = _get_organizations_all_from_db()
        task_set_cache_organizations_all(organization=organizations)

    filtered_organizations, filter_name, params = _get_filtered_organizations(
        organizations=organizations, data=data)

    return filtered_organizations, filter_name, params


def _get_filtered_organizations(
        organizations: QuerySet['Organizations'], data: QueryDict):

    params = data.urlencode()
    filter_class = OrganizationFilter
    filter_name = CACHE_KEY_FILTER_NAME.format(filter_name=f'organizations_all_{params}')

    filtered_organizations, filter_form = _create_filtered_object(
        queryset=organizations, data=data,
        filter_class=filter_class, filter_name=filter_name)

    return filtered_organizations, filter_form, params


def get_organization_info(organization_id: int):
    organization = _get_organization_object_from_db(organization_id=organization_id)

    return organization


# CRUD Event
def get_events_all(user_session_key: str, data: QueryDict,
                   user: 'AUTH_USER_MODEL' = None):

    events = _get_events_all_from_cache()
    if events is None:
        events = _get_events_all_from_db()
        task_set_cache_events_all(events=events)

    filtered_events, filter_form, params = _get_filtered_events(events=events, data=data)

    user_object = _get_user_object(user_session_key=user_session_key, user=user)

    if user_object:
        user = user_object.get('user').pk
        assigned_user_events = _get_assigned_user_events(user_id=user)
        filtered_events = _set_field_assigned(events=filtered_events, assigned_events_user=assigned_user_events)

    return filtered_events, filter_form, params, user


def _get_filtered_events(events: QuerySet['Events'], data: QueryDict):

    params = data.urlencode()
    filter_name = CACHE_KEY_FILTER_NAME.format(filter_name=f'events_all_{params}')
    filter_class = EventsFilter

    filtered_events, filter_form = _create_filtered_object(
        queryset=events, data=data,
        filter_class=filter_class,
        filter_name=filter_name
    )

    return filtered_events, filter_form, params


def get_event_card(event_id: int):

    event = _get_event_card_from_db(event_id=event_id)
    return event


def get_organization_events(organization_id: int, data: QueryDict):

    events_organization = _get_organization_events_from_db(organization_id=organization_id)
    params = data.urlencode()

    filtered_organization_events, filter_form = _create_filtered_object(
        queryset=events_organization,
        filter_class=OrganizationEventsFilter,
        data=data)

    return filtered_organization_events, filter_form, params


def get_organization_employees(organization_id: int):
    organization_employees = _get_organization_employees(organization_id=organization_id)
    return organization_employees


def get_user_events(user: 'AUTH_USER_MODEL', user_session_key: str,
                    data: QueryDict):

    user_id = _get_user_object(
        user_session_key=user_session_key, user=user).get('user').pk

    user_events = _get_user_events_with_assigned_field_for_profile(user_id=user_id)

    filtered_user_events, filter_form, params = (
        _get_filtered_user_events(user_events=user_events, data=data)
    )
    return filtered_user_events, filter_form, params, user_id


def _get_assigned_user_events(user_id: int):

    assigned_user_events = _get_assigned_user_events_from_cache(user_id=user_id)

    if assigned_user_events is None:
        assigned_user_events = dict(_get_assigned_user_events_from_db(user_id=user_id))
        task_set_cache_assigned_user_events(assigned_user_events=assigned_user_events, user_id=user_id)

    return assigned_user_events


def _set_field_assigned(events: QuerySet | list, assigned_events_user: dict) -> QuerySet | list:

    for event in events:
        event.assigned = True if assigned_events_user.get(event.id) else False

    return events


def get_event_and_event_records_for_customer(
        user_session_key: str, data: QueryDict,
        event_id: int, user: 'AUTH_USER_MODEL' = None):

    user_object = _get_user_object(
        user_session_key=user_session_key, user=user
    )
    event = _get_event_card_from_db(event_id=event_id)

    if user_object:
        user = user_object.get('user').pk

        event_records = (
            _get_event_records_with_registered_user_field(
                event_id=event_id, user_id=user)
        )
    else:
        event_records = (
            _get_event_records(event_id=event_id)
        )

    event_records, filter_form, params = (
        _get_filtered_event_records(event_records=event_records, data=data)
    )

    return event, event_records, filter_form, params, user


def _get_filtered_event_records(
        event_records: QuerySet, data: QueryDict) -> tuple[QuerySet['Records'], 'Form', str]:

    filter_class = EventRecordsListFilter
    params = data.urlencode()

    filtered_event_records, filter_form = _create_filtered_object(
        queryset=event_records, data=data,
        filter_class=filter_class)

    return filtered_event_records, filter_form, params


def _get_filtered_user_events(user_events: QuerySet['Events'], data: QueryDict):

    filter_class = EventsListUserFilter
    params = data.urlencode()
    filtered_user_events, filter_form = _create_filtered_object(
        queryset=user_events, filter_class=filter_class,
        data=data)

    return filtered_user_events, filter_form, params


@transaction.atomic
def set_assigned_event_to_user(
        user: 'AUTH_USER_MODEL', user_session_key: str, event_id: int):

    user_id = _get_user_object(
        user_session_key=user_session_key, user=user).get('user').pk

    assigned_event = AssignedEvents.objects.create(user_id=user_id, event_id=event_id)
    task_delete_assigned_user_events_from_cache(user_id=user_id)

    return assigned_event, user_id


@transaction.atomic
def delete_assigned_event_from_db(
        user: 'AUTH_USER_MODEL', user_session_key: str, event_id: int):

    user_id = _get_user_object(
        user_session_key=user_session_key, user=user).get('user').pk

    deleted_event = (
        AssignedEvents.objects.filter(user_id=user_id, event_id=event_id).delete()
    )
    task_delete_assigned_user_events_from_cache(user_id=user_id)

    return deleted_event


@transaction.atomic
def delete_event_and_all_records_user_from_db(user_id: int, event_id: int):

    recordings_user = (Recordings.objects.select_related('record')
                       .filter(user_id=user_id,
                               record__events__id=event_id))

    (AssignedEvents.objects.filter(user_id=user_id,
                                   event_id=event_id)
     .delete())

    task_delete_assigned_user_events_from_cache(user_id=user_id)

    id_records = (recording.record.id for recording in recordings_user)
    recordings_user.delete()

    (Records.objects.filter(id__in=id_records)
     .update(quantity_clients=F('quantity_clients') - 1))


def delete_event_from_cache(event_id: int):

    cache_key_event = CACHE_KEY_MODEL_OBJECT_ID.format(model='Events', object_id=event_id)
    cache.delete(cache_key_event)


# CRUD Record
def get_user_records_in_event(user_id: int, event_id: int,
                              data: QueryDict) -> tuple[list, Form, str]:

    user_records_in_event = _get_user_records_in_event_from_db(
        event_id=event_id, user_id=user_id)

    user_records_in_event, filter_form = _create_filtered_object(
        queryset=user_records_in_event, data=data,
        filter_class=UserRecordsInEventFilter)

    params = data.urlencode()

    return user_records_in_event, filter_form, params


def get_event_records_for_user_profile(user_id: int, event_id: int,
                                       data: QueryDict):

    event_records = _get_event_records_with_registered_user_field(user_id=user_id, event_id=event_id)
    filtered_event_records, filter_form = _create_filtered_object(
        queryset=event_records,
        filter_class=UserRecordsInEventFilter,
        data=data
    )
    params = data.urlencode()

    return filtered_event_records, filter_form, params


@transaction.atomic
def sign_up_for_event(user: 'AUTH_USER_MODEL', user_session_key: str,
                      record_id: int):

    user_object = _get_user_object(
            user_session_key=user_session_key, user=user)

    if user_object:
        user_id = user_object.get('user').pk

        record = Records.objects.filter(id=record_id)

        Recordings.objects.create(record_id=record_id,
                                  user_id=user_id,
                                  status_recording=StatusRecordingChoices.PAID)

        task_delete_records_all_from_cache()

        record.update(quantity_clients=F('quantity_clients') + 1)

        record = record.get()
        # quantity_clients = record.get('quantity_clients')

        return record


@transaction.atomic
def cancel_recording(user: 'AUTH_USER_MODEL', user_session_key: str,
                     record_id: int):

    user_id = _get_user_object(
        user_session_key=user_session_key, user=user).get('user').pk

    record = Records.objects.filter(id=record_id)
    Recordings.objects.filter(user=user_id, record=record_id).delete()
    record.update(quantity_clients=F('quantity_clients') - 1)
    record = record.get()

    return record, user_id


@transaction.atomic
def delete_recording_user_form_profile(user_id: int, record_id: int):

    record = Records.objects.filter(id=record_id)

    user_recordings = Recordings.objects.filter(user=user_id, record=record_id)
    unique_cache_key_records_objects = CACHE_KEY_MODEL_OBJECT_ID.format(model_name='Records', object_id=record_id)
    cache.delete(unique_cache_key_records_objects)
    user_recordings.delete()
    record.update(quantity_clients=F('quantity_clients') - 1)







