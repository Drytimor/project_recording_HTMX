from django.db.models import Prefetch
from customer.models import Recordings
from organization.models import Organizations, Employees, Events, Records
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
    organization.events.all().delete()
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
    event = (Events.objects.filter(id=event_id)
                           .prefetch_related(
                            Prefetch(lookup='employees',
                                     to_attr='employees_event'))
                           .get())
    return event


@transaction.atomic
def update_event_in_db(event, form):
    data = form.cleaned_data
    event_employees = data.pop('employees')
    Events.objects.filter(id=event.pk).update(**data)
    event.employees.set(event_employees)


def delete_event_from_db(event):
    event.delete()


@transaction.atomic
def create_record_in_db(event_id, form):
    data = form.cleaned_data
    data['events_id'] = event_id
    record = Records.objects.create(**data)
    return record


def get_event_and_all_records_from_db_for_customer(user_id, event_id):

    event = (Events.objects.filter(id=event_id)
                           .prefetch_related(
                            Prefetch(lookup='employees',
                                     to_attr='employees_event'))
                           .get())
    if user_id:
        records = event.records.prefetch_related(
                                   Prefetch(lookup='recordings',
                                            queryset=Recordings.objects.select_related('user')
                                                                       .only('user_id'),
                                            to_attr='user_recordings'))

        # цикл проходит по всем записям зарегистрированных пользователей на мероприятие
        # если не находит там id вошедшего пользователя
        # добавляет в queryset поле registered_user в True,
        # иначе устанавливает registered_user в False

        for recordings in records:
            registered_user_flag = any(user_id == _recordings.user.id for _recordings in recordings.user_recordings)
            recordings.registered_user = registered_user_flag
    else:
        records = event.records.all()
    return event, records


def get_event_and_all_records_from_db_for_organization(event_id):

    event = (Events.objects.filter(id=event_id)
                           .prefetch_related(
                            Prefetch(lookup='records',
                                     to_attr='records_event'),
                            Prefetch(lookup='employees',
                                     to_attr='employees_event'))
                           .get())

    return event


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
