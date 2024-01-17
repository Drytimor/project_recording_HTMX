from django.db.models import F, Prefetch, Count
from django.db import transaction
from allauth_app.settings import CACHE_KEY_USER_ASSIGNED_EVENTS, CACHE_KEY_EVENT_ID
from customer.filters import EventsFilter
from customer.models import StatusRecordingChoices, Recordings, AssignedEvents
from organization.models import Organizations, Events, Records
from organization.todo import create_card_record_user, set_field_assigned
from django.core.cache import cache


def get_or_set_assigned_user_events_from_cache(user_id, set_cache=True):

    cache_key_user_assigned_events = CACHE_KEY_USER_ASSIGNED_EVENTS.format(user_id=user_id)
    assigned_events_user = cache.get(key=cache_key_user_assigned_events)

    if assigned_events_user is None:
        assigned_events_user = (AssignedEvents.objects.filter(user_id=user_id)
                                .values_list('event__id'))
        if set_cache:
            cache.set(key=cache_key_user_assigned_events,
                      value=assigned_events_user,
                      timeout=60 ** 2 * 6)

    return assigned_events_user


def delete_assigned_user_events_from_cache(user_id):
    cache_key_user_assigned_events = CACHE_KEY_USER_ASSIGNED_EVENTS.format(user_id=user_id)
    cache.delete(cache_key_user_assigned_events)


def delete_event_from_cache(event_id):
    cache_key_event = CACHE_KEY_EVENT_ID.format(event_id=event_id)
    cache.delete(cache_key_event)


def get_organizations_all_from_db():
    organizations = Organizations.objects.select_related('category').all()
    if len(organizations) > 0:
        return organizations


def get_organization_info_from_db(organization_id):
    organization = Organizations.objects.select_related('category').get(id=organization_id)
    return organization


def _get_all_events_gen(events):
    all_events = ((event.id, event) for event in events)
    yield from all_events


def _get_id_events_gen(events):
    id_events = (event.id for event in events)
    yield from id_events


def get_events_all_from_db(user_id):
    """Возвращает список всех мероприятий из кеша либо из базы"""

    events_from_db = cache.get_or_set(key='events_all',
                                      default=Events.objects.select_related('organization'),
                                      timeout=60)

    cache_key_event = CACHE_KEY_EVENT_ID
    events_id = _get_id_events_gen(events_from_db)
    events = list(cache.get_many(keys=[cache_key_event.format(event_id=_id) for _id in events_id]).values())

    if not events:
        events_all = _get_all_events_gen(events_from_db)
        cache.set_many({cache_key_event.format(event_id=_id): _event for _id, _event in events_all}, timeout=60)
        events = events_from_db

    if user_id:
        assigned_events_user = get_or_set_assigned_user_events_from_cache(user_id=user_id)

        events = set_field_assigned(events=events,
                                    assigned_events_user=assigned_events_user)
    return events


def get_all_events_using_filter(user_id, data):

    events = cache.get_or_set(key='events_all',
                              default=Events.objects.select_related('organization'),
                              timeout=60)

    cache_key_event = CACHE_KEY_EVENT_ID

    filter_events = EventsFilter(data=data,
                                 queryset=events,
                                 filter_name='events_all')
    events = filter_events.qs

    if user_id:
        assigned_events_user = get_or_set_assigned_user_events_from_cache(user_id=user_id)

        events = set_field_assigned(events=events,
                                    assigned_events_user=assigned_events_user)

    cache.set_many({cache_key_event.format(event_id=event.id): event for event in events}, timeout=60)

    return events


@transaction.atomic
def assigned_event_to_user(user_id, event_id):
    if user_id:
        assigned_event = AssignedEvents.objects.create(user_id=user_id,
                                                       event_id=event_id)

        delete_assigned_user_events_from_cache(user_id=user_id)

        return assigned_event


@transaction.atomic
def delete_assigned_event_from_db(user_id, event_id):
    deleted_event = (AssignedEvents.objects.filter(user_id=user_id,
                                                   event_id=event_id)
                                           .delete())

    delete_assigned_user_events_from_cache(user_id=user_id)

    return True if deleted_event else False


def get_event_card_from_db(event_id):

    event = (Events.objects.filter(id=event_id)
                           .prefetch_related(
                            Prefetch(lookup='employees',
                                     to_attr='employees_event')))
    return event.get()


def get_user_events_from_db(user_id):
    user_events_id = (Recordings.objects
                                .values_list('record__events__id')
                                .filter(user_id=user_id))

    assigned_events_user = get_or_set_assigned_user_events_from_cache(user_id=user_id)

    user_events = (Events.objects
                         .select_related('organization')
                         .prefetch_related(Prefetch('employees', to_attr='employees_event'))
                         .filter(id__in=user_events_id.union(assigned_events_user)))

    events = set_field_assigned(events=user_events,
                                assigned_events_user=assigned_events_user)

    return events


@transaction.atomic
def delete_event_and_all_records_user_from_db(user_id, event_id):
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


def get_user_records_from_db(user_id, event_id):
    user_recordings = (Recordings.objects.select_related('record')
                                         .filter(user_id=user_id,
                                                 record__events__id=event_id))
    user_records = (records.record for records in user_recordings)
    return user_records


def get_user_event_records_from_db(user_id, event_id):

    event_recordings = (Recordings.objects.filter(record__events__id=event_id)
                                  .select_related('user', 'record'))

    event_records = Records.objects.filter(events_id=event_id)
    records = create_card_record_user(user_id=user_id,
                                      event_recordings=event_recordings,
                                      event_records=event_records)
    return records


@transaction.atomic
def sign_up_for_event(user_id, record_id):
    if user_id:
        record = Records.objects.filter(id=record_id)
        Recordings.objects.create(record_id=record_id,
                                  user_id=user_id,
                                  status_recording=StatusRecordingChoices.PAID)

        record.update(quantity_clients=F('quantity_clients') + 1)
        return record.get()


@transaction.atomic
def cancel_recording(user_id, record_id):
    record = Records.objects.filter(id=record_id)
    Recordings.objects.filter(user=user_id, record=record_id).delete()
    record.update(quantity_clients=F('quantity_clients') - 1)
    return record.get()


@transaction.atomic
def delete_recording_user_form_profile(user_id, event_id, record_id):

    record = Records.objects.filter(id=record_id)
    user_recordings = (Recordings.objects.filter(user=user_id, record=record_id)
                                         .annotate(count_recordings=Count('user__recordings__id')))

    assigned_events_user = get_or_set_assigned_user_events_from_cache(user_id=user_id, set_cache=False)

    is_assigned_event = any(event_id in _id for _id in assigned_events_user)
    count_user_recordings = user_recordings[0].count_recordings

    user_recordings.delete()
    record.update(quantity_clients=F('quantity_clients') - 1)

