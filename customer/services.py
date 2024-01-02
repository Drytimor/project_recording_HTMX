from organization.models import Organizations, Events
from organization.todo import db_function, card_info_event


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


def get_event_card(event_id):
    event = (Events.objects.filter(id=event_id)
             .prefetch_related('employees', 'record')
             .select_related('organization')
             .order_by('-record__datetime')
             .get())
    employees = event.employees.all()
    records = event.record.all()
    organization = event.organization
    return organization, event, employees, records


def get_event_card_from_db(event_id):
    queryset = (Events.objects.filter(id=event_id)
                              .values('id', 'name', 'organization__id',
                                      'organization__name', 'employees__id',
                                      'employees__name'))
    event_card = card_info_event(queryset)
    return event_card
