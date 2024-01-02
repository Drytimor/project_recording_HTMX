from organization.models import Organizations, Employees, Events, Records
from organization.todo import db_function
from django.db import transaction


@transaction.atomic
def create_organization_from_db(user, form):
    data = form.cleaned_data
    data['user'] = user
    organization = Organizations.objects.create(**data)
    return organization


def get_organization_from_db(user_id=None, organization_id=None):
    if user_id:
        queryset = Organizations.objects.select_related('category').filter(user__id=user_id)
        organization = None
        try:
            organization = queryset.get()
        except queryset.model.DoesNotExist:
            pass
        return organization
    if organization_id:
        return Organizations.objects.select_related('category').get(id=organization_id)


@transaction.atomic
def update_organization_in_db(organization, form):
    data = form.cleaned_data
    Organizations.objects.select_related('category').filter(id=organization.pk).update(**data)


@transaction.atomic
def delete_organization_from_db(organization_id):
    organization = Organizations.objects.get(id=organization_id)
    for event in organization.events.all():
        event.record.all().delete()
    organization.delete()


@transaction.atomic
def create_employee_in_db(organization_id, form):
    data = form.cleaned_data
    data['organization_id'] = organization_id
    employees = Employees.objects.create(**data)
    return employees


def get_employees_from_db(organization_id=None, employee_id=None):
    if organization_id:
        employees_list = Employees.objects.filter(organization_id=organization_id)
        return employees_list
    elif employee_id:
        employee = Employees.objects.get(id=employee_id)
        return employee


@transaction.atomic
def update_employee_in_db(employee_id, form):
    data = form.cleaned_data
    Employees.objects.filter(id=employee_id).update(**data)


def delete_employee_from_db(employee):
    employee.delete()


@transaction.atomic
def create_event_in_db(organization_id, form):
    data = form.cleaned_data
    data['organization_id'] = organization_id
    event_employees = data.pop('employees')
    event = Events.objects.create(**data)
    event.employees.set(event_employees)
    return event


def get_events_from_db(organization_id=None, event_id=None):
    if organization_id:
        events = Events.objects.filter(organization_id=organization_id)
        return events
    if event_id:
        event = Events.objects.get(id=event_id)
        return event


def get_event_profile_from_db(event_id):
    queryset = (Events.objects.filter(id=event_id)
                              .values('id', 'name', 'organization__id', 'organization__name', 'employees__name'))
    event_profile = db_function(queryset)
    return event_profile


@transaction.atomic
def update_event_in_db(event, form):
    data = form.cleaned_data
    event_employees = data.pop('employees')
    Events.objects.filter(id=event.pk).update(**data)
    event.employees.set(event_employees)


def delete_event_from_db(event):
    event.record.all().delete()
    event.delete()


@transaction.atomic
def create_record_in_db(event, form):
    data = form.cleaned_data
    record = Records.objects.create(**data)
    event.record.add(record)
    return record


def get_event_and_all_records_from_db(event_id):
    event = (Events.objects.filter(id=event_id)
                           .prefetch_related('employees', 'record')
                           .order_by('-record__datetime')
                           .get())
    employees = event.employees.all()
    records = event.record.all()
    return event, employees, records


def get_record_from_db(record_id):
    if record_id:
        record = Records.objects.get(id=record_id)
        return record


@transaction.atomic
def update_record_in_db(record_id, form):
    data = form.cleaned_data
    Records.objects.filter(id=record_id).update(**data)


def delete_record_from_db(record_id):
    Records.objects.filter(id=record_id).delete()
