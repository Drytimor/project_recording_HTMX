from django.db.models import F

from customer.models import StatusRecordingChoices, Recordings
from organization.models import Organizations, Events, Records
from organization.todo import db_function, create_card_event


def get_organizations_all_from_db():
    organizations = Organizations.objects.select_related('category').all()
    if len(organizations) > 0:
        return organizations


def get_organization_info_from_db(organization_id):
    organization = Organizations.objects.select_related('category').get(id=organization_id)
    return organization


def get_events_all_from_db():
    events = Events.objects.select_related('organization').all()
    return events


def get_event_card_from_db(event_id):
    queryset = (Events.objects.filter(id=event_id)
                              .values('id', 'name', 'organization__id',
                                      'organization__name', 'employees__id',
                                      'employees__name'))
    event_card = create_card_event(queryset)
    return event_card


def get_user_records_from_db(user_id):
    user_recordings = Recordings.objects.select_related('record__events').filter(user_id=user_id)
    user_records = (records.record for records in user_recordings)
    return user_records


def sign_up_for_event(user_id, record_id):
    record = Records.objects.filter(id=record_id)
    Recordings.objects.create(record_id=record_id,
                              user_id=user_id,
                              status_recording=StatusRecordingChoices.PAID)

    record.update(quantity_clients=F('quantity_clients') + 1)
    return record.get()


def cancel_recording(user_id, record_id):
    record = Records.objects.filter(id=record_id)
    Recordings.objects.filter(user=user_id, record=record_id).delete()
    record.update(quantity_clients=F('quantity_clients') - 1)
    return record.get()


def delete_recording_user_form_profile(user_id, record_id):
    record = Records.objects.filter(id=record_id)
    Recordings.objects.filter(user=user_id, record=record_id).delete()
    record.update(quantity_clients=F('quantity_clients') - 1)

