from django.http import HttpResponse
from django.views.generic.base import View, ContextMixin, TemplateResponseMixin

from customer.services import (get_organizations_all_from_db, get_events_all_from_db, get_organization_info_from_db,
                               get_event_card_from_db, sign_up_for_event, cancel_recording, get_user_records_from_db,
                               delete_recording_user_form_profile)

from organization.mixins import CustomTemplateResponseMixin, CustomMixin
from organization.services import (get_employees_from_db, get_events_from_db, get_event_and_all_records_from_db_for_customer)


# CRUD organization

class OrganizationsAll(CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'organizations/organization_all.html'
    response_htmx = True
    organizations = None

    def get(self, *args, **kwargs):
        self.organizations = get_organizations_all_from_db()
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.organizations:
            context['organizations_all'] = self.organizations
        return context


organizations_all = OrganizationsAll.as_view()


class OrganizationInfo(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'organizations/organization_info.html'
    response_htmx = True
    organization = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.organization = get_organization_info_from_db(organization_id=self.organization_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'organization_id': 'pk'
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.organization:
            context['organization'] = self.organization
        if self.organization_id:
            context['organization_id'] = self.organization_id
        return context


organization_info = OrganizationInfo.as_view()


class OrganizationEvents(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'events/org_events.html'
    response_htmx = True
    events = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.events = get_events_from_db(organization_id=self.organization_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'organization_id': 'pk'
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.events:
            context['events'] = self.events
        if self.organization_id:
            context['organization_id'] = self.organization_id
        return context


organization_events = OrganizationEvents.as_view()


class OrganizationEmployees(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'employees/org_employees.html'
    response_htmx = True
    employees = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.employees = get_employees_from_db(organization_id=self.organization_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'organization_id': 'pk'
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.employees:
            context['employees'] = self.employees
        if self.organization_id:
            context['organization_id'] = self.organization_id
        return context


organization_employees = OrganizationEmployees.as_view()


# CRUD Employees
class EmployeeInfo(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'employees/employee_info.html'
    response_htmx = True
    employee = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.employee = get_employees_from_db(employee_id=self.employee_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'employee_id': 'pk',
            'organization_id': 'org_pk'
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.employee:
            context['employee'] = self.employee
        if self.organization_id:
            context['organization_id'] = self.organization_id
        return context


employee_info = EmployeeInfo.as_view()


# CRUD Event
class EventsAll(CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'events/events_all.html'
    response_htmx = True
    events = None

    def get(self, *args, **kwargs):
        self.events = get_events_all_from_db()
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.events:
            context['events'] = self.events
        return context


events_all = EventsAll.as_view()


class EventInfo(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'events/event_info.html'
    response_htmx = True
    event = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.event = get_event_card_from_db(event_id=self.event_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'event_id': 'pk',
            'organization_id': 'org_pk'
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.event:
            context['event'] = self.event
        if self.organization_id:
            context['organization_id'] = self.organization_id
        return context


event_info = EventInfo.as_view()


class EventRecords(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'records/event_records.html'
    response_htmx = True
    records = None
    event = None
    employees = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.event, self.employees, self.records = get_event_and_all_records_from_db_for_customer(user_id=self.user_id,
                                                                                     event_id=self.event_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'event_id': 'pk',
            'organization_id': 'org_pk',
            'user_id': 'user_pk'
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.records:
            context['records'] = self.records
        if self.event:
            context['event'] = self.event
        if self.employees:
            context['employees'] = self.employees
        if self.organization_id:
            context['organization_id'] = self.organization_id
        if self.user_id:
            context['user_pk'] = self.user_id
        return context


event_records = EventRecords.as_view()


# CRUD Records
class RecordSignUp(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'records/record_sign_up.html'
    response_htmx = True
    record = None

    def put(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.record = sign_up_for_event(user_id=self.user_id, record_id=self.record_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'record_id': 'pk',
            'user_id': 'user_pk'
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.record:
            context['record'] = self.record
        if self.user_id:
            context['user_pk'] = self.user_id
        return context


record_sign_up = RecordSignUp.as_view()


class RecordCancel(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'records/record_cancel.html'
    response_htmx = True
    record = None

    def put(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.record = cancel_recording(user_id=self.user_id, record_id=self.record_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'record_id': 'pk',
            'user_id': 'user_pk'
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.record:
            context['record'] = self.record
        if self.user_id:
            context['user_pk'] = self.user_id
        return context


record_cancel = RecordCancel.as_view()


class RecordsUser(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'records/user_records.html'
    response_htmx = True
    user_records = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.user_records = get_user_records_from_db(user_id=self.user_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'user_id': 'pk'
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.user_records:
            context['user_records'] = self.user_records
        if self.user_id:
            context['user_pk'] = self.user_id
        return context


records_user = RecordsUser.as_view()


class RecordUserDelete(CustomMixin, TemplateResponseMixin, ContextMixin, View):

    def delete(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        delete_recording_user_form_profile(record_id=self.record_id, user_id=self.user_id)
        return HttpResponse(status=200)

    def get_attr_from_request(self):
        attr = {
            'record_id': 'pk',
            'user_id': 'user_pk'
        }
        return attr


record_user_delete = RecordUserDelete.as_view()