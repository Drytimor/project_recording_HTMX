from django.db.models import F, Prefetch, Count, Q
from django.db import transaction
from allauth_app.settings import CACHE_KEY_USER_ASSIGNED_EVENTS, CACHE_KEY_MODEL_OBJECT_ID, \
    CACHE_KEY_ALL_OBJECT_FROM_DB, CACHE_KEY_FILTER_NAME
from customer.filters import EventsFilter, OrganizationFilter, RecordsListUserFilter
from customer.models import StatusRecordingChoices, Recordings, AssignedEvents
from organization.models import Organizations, Events, Records
from organization.todo import create_card_record_user
from django.core.cache import cache
from django.db.models.query import QuerySet
from django.http.request import QueryDict
from django.forms import Form


# def get_model_objects_from_cache(
#         cache_key_all_objects: str,
#         unique_cache_key_objects: str,
#         queryset_from_db: QuerySet,
#         timeout_from_cache: int = 60) -> QuerySet | list:
#
#     queryset = cache.get_or_set(key=cache_key_all_objects,
#                                 default=queryset_from_db,
#                                 timeout=timeout_from_cache)
#
#     model_object_from_cache = cache.get_many(
#         keys=[unique_cache_key_objects.format(model=_object.__class__.__name__, object_id=_object.id) for _object in
#               queryset]
#     ).values()
#
#     if not model_object_from_cache:
#         cache.set_many(
#             {unique_cache_key_objects.format(model=_object.__class__.__name__,
#                                              object_id=_object.id): _object for _object in queryset},
#             timeout=timeout_from_cache)
#
#         return queryset
#
#     return list(model_object_from_cache)


def get_filters_model_objects_from_cache(
        data: QueryDict,
        filter_name: str,
        filter_class,
        cache_key_all_objects: str,
        queryset_from_db: QuerySet,
        timeout_from_cache: int = 60*5) -> tuple[list, Form]:

    queryset = cache.get_or_set(key=cache_key_all_objects,
                                default=queryset_from_db,
                                timeout=timeout_from_cache)

    filter_objects = filter_class(data=data,
                                  queryset=queryset,
                                  filter_name=filter_name)

    filtered_objects = filter_objects.qs
    filter_form = filter_objects.form

    return filtered_objects, filter_form


# CRUD Organization
def get_all_organization_using_filter(data: QueryDict) -> tuple[list, Form, str]:

    cache_key_organization_all = CACHE_KEY_ALL_OBJECT_FROM_DB.format(model='Organizations')
    params = data.urlencode()
    cache_key_filter_name = CACHE_KEY_FILTER_NAME.format(filter_name=f'organizations_all_{params}')
    organization_from_db = Organizations.objects.select_related('category')

    filtered_organizations, filter_form = get_filters_model_objects_from_cache(
        data=data,
        filter_name=cache_key_filter_name,
        filter_class=OrganizationFilter,
        cache_key_all_objects=cache_key_organization_all,
        queryset_from_db=organization_from_db
    )

    return filtered_organizations, filter_form, params


def get_organization_info_from_db(organization_id: int):
    organization = Organizations.objects.select_related('category').get(id=organization_id)

    return organization


# CRUD Event
def get_all_events_using_filter(user_id: int, data: QueryDict) -> tuple[list, Form, str]:

    cache_key_events_all = CACHE_KEY_ALL_OBJECT_FROM_DB.format(model='Events')
    params = data.urlencode()
    cache_key_filter_name = CACHE_KEY_FILTER_NAME.format(filter_name=f'events_all_{params}')
    events_from_db = Events.objects.select_related('organization')

    filtered_events, filter_form = get_filters_model_objects_from_cache(
        data=data,
        filter_name=cache_key_filter_name,
        filter_class=EventsFilter,
        cache_key_all_objects=cache_key_events_all,
        queryset_from_db=events_from_db,
        )

    if user_id:
        filtered_events_with_field_assigned = sets_in_events_filed_assigned(user_id=user_id, events=filtered_events)

        return filtered_events_with_field_assigned, filter_form, params

    return filtered_events, filter_form, params


def get_event_card_from_db(event_id: int):

    event = (Events.objects.filter(id=event_id)
                           .prefetch_related(
                           Prefetch(lookup='employees',
                                    to_attr='employees_event')))

    return event.get()


def get_user_events_from_db(user_id: int):
    user_events_id = (Recordings.objects
                      .values_list('record__events__id')
                      .filter(user_id=user_id))

    assigned_events_user = get_or_set_assigned_user_events_from_cache(user_id=user_id)

    user_events = (Events.objects
                   .select_related('organization')
                   .prefetch_related(Prefetch('employees', to_attr='employees_event'))
                   .filter(Q(id__in=user_events_id) | Q(id__in=assigned_events_user)))

    events = set_field_assigned(events=user_events,
                                assigned_events_user=assigned_events_user)

    return events


@transaction.atomic
def assigned_event_to_user(user_id: int, event_id: int):

    if user_id:
        assigned_event = AssignedEvents.objects.create(user_id=user_id,
                                                       event_id=event_id)

        delete_assigned_user_events_from_cache(user_id=user_id)

        return assigned_event


@transaction.atomic
def delete_assigned_event_from_db(user_id: int, event_id: int):
    deleted_event = (AssignedEvents.objects.filter(user_id=user_id,
                                                   event_id=event_id)
                     .delete())

    delete_assigned_user_events_from_cache(user_id=user_id)

    return True if deleted_event else False


@transaction.atomic
def delete_event_and_all_records_user_from_db(user_id: int, event_id: int):
    recordings_user = (Recordings.objects.select_related('record')
                       .filter(user_id=user_id,
                               record__events__id=event_id))

    (AssignedEvents.objects.filter(user_id=user_id,
                                   event_id=event_id)
     .delete())

    delete_assigned_user_events_from_cache(user_id=user_id)

    id_records = (recording.record.id for recording in recordings_user)
    recordings_user.delete()

    (Records.objects.filter(id__in=id_records)
     .update(quantity_clients=F('quantity_clients') - 1))


def get_or_set_assigned_user_events_from_cache(user_id: int) -> dict:

    cache_key_user_assigned_events = CACHE_KEY_USER_ASSIGNED_EVENTS.format(user_id=user_id)
    assigned_events_user_from_cache = cache.get(key=cache_key_user_assigned_events)

    if assigned_events_user_from_cache is None:

        assigned_events_user_from_db = dict(
            AssignedEvents.objects.filter(user_id=user_id)
                                  .values_list('event', 'user')
        )

        cache.set(key=cache_key_user_assigned_events,
                  value=assigned_events_user_from_db,
                  timeout=60**2 * 6)

        return assigned_events_user_from_db

    return assigned_events_user_from_cache


def set_field_assigned(events: QuerySet | list, assigned_events_user: dict) -> QuerySet | list:

    for event in events:
        event.assigned = True if assigned_events_user.get(event.id) else False

    return events


def sets_in_events_filed_assigned(user_id: int, events: QuerySet | list) -> QuerySet | list:

    assigned_events_user = get_or_set_assigned_user_events_from_cache(user_id=user_id)

    events_with_field_assigned = set_field_assigned(events=events,
                                                    assigned_events_user=assigned_events_user)

    return events_with_field_assigned


def delete_assigned_user_events_from_cache(user_id: int):

    cache_key_user_assigned_events = CACHE_KEY_USER_ASSIGNED_EVENTS.format(user_id=user_id)
    cache.delete(cache_key_user_assigned_events)


def delete_event_from_cache(event_id: int):

    cache_key_event = CACHE_KEY_MODEL_OBJECT_ID.format(model='Events', object_id=event_id)
    cache.delete(cache_key_event)


# CRUD Record
def get_user_records_from_db(
        user_id: int,
        event_id: int,
        data: QueryDict) -> tuple[list, Form, str]:

    list_user_records_id = (Recordings.objects.filter(user_id=user_id,
                                                      record__events__id=event_id)
                                              .values_list('record', flat=True))

    user_records_from_db = Records.objects.filter(id__in=list_user_records_id)

    user_records_filter = RecordsListUserFilter(data=data,
                                                queryset=user_records_from_db)

    filter_form = user_records_filter.form
    user_records = user_records_filter.qs

    params = data.urlencode()

    return user_records, filter_form, params


def get_user_event_records_from_db(user_id: int, event_id: int):

    event_recordings = (Recordings.objects.filter(record__events__id=event_id)
                                  .select_related('user', 'record'))

    event_records = Records.objects.filter(events_id=event_id)

    records = create_card_record_user(user_id=user_id,
                                      event_recordings=event_recordings,
                                      event_records=event_records)
    return records


@transaction.atomic
def sign_up_for_event(user_id: int, record_id: int):

    if user_id:
        record = Records.objects.filter(id=record_id)

        Recordings.objects.create(record_id=record_id,
                                  user_id=user_id,
                                  status_recording=StatusRecordingChoices.PAID)

        unique_cache_key_records_objects = CACHE_KEY_ALL_OBJECT_FROM_DB.format(model='Records')
        cache.delete(unique_cache_key_records_objects)

        record.update(quantity_clients=F('quantity_clients') + 1)

        return record.get()


@transaction.atomic
def cancel_recording(user_id: int, record_id: int):

    record = Records.objects.filter(id=record_id)
    Recordings.objects.filter(user=user_id, record=record_id).delete()
    record.update(quantity_clients=F('quantity_clients') - 1)

    return record.get()


@transaction.atomic
def delete_recording_user_form_profile(user_id: int, record_id: int):

    record = Records.objects.filter(id=record_id)

    user_recordings = Recordings.objects.filter(user=user_id, record=record_id)
    unique_cache_key_records_objects = CACHE_KEY_MODEL_OBJECT_ID.format(model='Records', object_id=record_id)
    cache.delete(unique_cache_key_records_objects)
    user_recordings.delete()
    record.update(quantity_clients=F('quantity_clients') - 1)

