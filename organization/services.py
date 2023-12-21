from django.http import Http404
from django.utils.translation import gettext as _
from organization.models import Organizations, Employees, Events, EventRecords
from organization.todo import db_function
from django.db import transaction


@transaction.atomic
def create_organization_from_db(user, form, organization_created=True):
    data = form.cleaned_data
    data['user'] = user
    user.organization_created = organization_created
    user.save(update_fields=['organization_created'])
    organization = Organizations.objects.create(**data)
    return organization


def get_organization_from_db(user=None, organization_id=None):
    if user and user.organization_created:
        queryset = Organizations.objects.select_related('category').filter(user=user)
        try:
            organization = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                _("No %(verbose_name)s found matching the query")
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return organization
    if organization_id:
        return Organizations.objects.get(id=organization_id)


@transaction.atomic
def update_organization_in_db(organization, form):
    data = form.cleaned_data
    Organizations.objects.filter(id=organization.pk).update(**data)


@transaction.atomic
def delete_organization_from_db(user, organization_created=False):
    user.organizations.delete()
    user.organization_created = organization_created
    user.save(update_fields=['organization_created'])


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
def update_employee_in_db(employee, form):
    data = form.cleaned_data
    Employees.objects.filter(id=employee.pk).update(**data)


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
                              .values('id', 'name', 'employees__name'))
    event_profile = db_function(queryset)
    return event_profile


@transaction.atomic
def update_event_in_db(event, form):
    data = form.cleaned_data
    event_employees = data.pop('employees')
    Events.objects.filter(id=event.pk).update(**data)
    event.employees.set(event_employees)


def delete_event_from_db(event):
    event.event_records.all().delete()
    event.delete()


@transaction.atomic
def create_record_in_db(event, form):
    data = form.cleaned_data
    record = EventRecords.objects.create(**data)
    record.event.add(event)
    return record


def get_records_from_db(event_id):
    records = (EventRecords.objects
                           .filter(event__id=event_id)
                           .order_by('-datetime')
                           .values('limit_clients', 'quantity_clients', 'datetime'))
    if len(records) > 0:
        return records
