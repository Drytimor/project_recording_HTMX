from organization.models import Organizations, Events
from organization.todo import db_function


def get_organizations_all_from_db():
    organizations = Organizations.objects.select_related('category').all()
    if len(organizations) > 0:
        return organizations


def get_events_all_from_db():
    events = Events.objects.values('id', 'name', 'employees__name', 'limit_clients', 'quantity_clients')
    events_all = db_function(events)
    if len(events) > 0:
        return events_all

