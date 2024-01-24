from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View, ContextMixin, TemplateResponseMixin

from customer.filters import RecordsListUserFilter
from customer.services import (get_organization_info_from_db,
                               get_event_card_from_db, sign_up_for_event, cancel_recording, get_user_records_from_db,
                               delete_recording_user_form_profile, get_user_events_from_db,
                               get_user_event_records_from_db, assigned_event_to_user, delete_assigned_event_from_db,
                               delete_event_and_all_records_user_from_db, get_all_events_using_filter,
                               get_all_organization_using_filter)

from organization.mixins import CustomTemplateResponseMixin, CustomMixin
from organization.services import (get_employees_from_db, get_events_from_db, get_event_and_all_records_from_db_for_customer)
from django.views.generic import ListView


# CRUD organization
class OrganizationsAll(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'organizations/organization_all.html'
    response_htmx = True
    organizations = None
    filter_form = None
    params = None

    def get(self, *args, **kwargs):
        self.organizations, self.filter_form, self.params = get_all_organization_using_filter(data=self.request.GET)
        self.page_obj, self.elided_page_range = self.create_pagination(object_list=self.organizations)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.organizations:
            context.update({
                'organizations': self.page_obj.object_list,
                'filter_form': self.filter_form,
                'params': self.params,
                'page_obj': self.page_obj,
                'elided_page_range': self.elided_page_range,
            })

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
class EventsAll(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'events/events_all.html'
    response_htmx = True
    events = None
    filter_form = None
    params = None

    def get(self, *args, **kwargs):
        self.user_id = self.get_or_set_user_id_from_cache()

        self.events, self.filter_form, self.params = get_all_events_using_filter(user_id=self.user_id,
                                                                                 data=self.request.GET)

        self.page_obj, self.elided_page_range = self.create_pagination(object_list=self.events)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.events:
            context.update({
                'events': self.page_obj.object_list,
                'user_pk': self.user_id,
                'filter_form': self.filter_form,
                'params': self.params,
                'page_obj': self.page_obj,
                'elided_page_range': self.elided_page_range,
            })

        return context


events_all = EventsAll.as_view()


class AssignedEvents(CustomMixin, TemplateResponseMixin, ContextMixin, View):

    template_name = 'events/htmx/assigned_event.html'
    assigned_event = None
    deleted_event = None

    def put(self, *args, **kwargs):
        self.user_id = self.get_or_set_user_id_from_cache()
        self.set_class_attributes_from_request()
        self.assigned_event = assigned_event_to_user(user_id=self.user_id,
                                                     event_id=self.event_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def delete(self, *args, **kwargs):
        self.user_id = self.get_or_set_user_id_from_cache()
        self.set_class_attributes_from_request()
        self.deleted_event = delete_assigned_event_from_db(user_id=self.user_id,
                                                           event_id=self.event_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'event_id': 'event_pk'
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.assigned_event:
            context['assigned_event'] = self.assigned_event
        if self.deleted_event:
            context['deleted_event'] = self.deleted_event
        if self.user_id:
            context['user_pk'] = self.user_id
        if self.event_id:
            context['event_pk'] = self.event_id
        return context


assigned_events = AssignedEvents.as_view()


class EventsListUser(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'events/user_events.html'
    response_htmx = True
    user_events = None

    def get(self, *args, **kwargs):
        self.user_id = self.get_or_set_user_id_from_cache()
        self.user_events = get_user_events_from_db(user_id=self.user_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.user_events:
            context['user_events'] = self.user_events
        if self.user_id:
            context['user_pk'] = self.user_id
        return context


events_user = EventsListUser.as_view()


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
    event = None
    records = None

    def get(self, *args, **kwargs):
        self.user_id = self.get_or_set_user_id_from_cache()
        self.set_class_attributes_from_request()
        self.event, self.records = get_event_and_all_records_from_db_for_customer(user_id=self.user_id,
                                                                                  event_id=self.event_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'event_id': 'event_pk',
            'organization_id': 'org_pk',
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.event:
            context['event'] = self.event
        if self.records:
            context['records'] = self.records
        if self.organization_id:
            context['organization_id'] = self.organization_id
            context['user_pk'] = self.user_id
        return context


event_records = EventRecords.as_view()


# CRUD Records
class RecordSignUp(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'records/record_sign_up.html'
    response_htmx = True
    record = None

    def put(self, *args, **kwargs):
        self.user_id = self.get_or_set_user_id_from_cache()
        self.set_class_attributes_from_request()
        self.record = sign_up_for_event(user_id=self.user_id, record_id=self.record_id)
        context = self.get_context_data()
        headers = self.set_headers_to_response()
        return self.render_to_response(context=context,
                                       headers=headers)

    def set_headers_to_response(self):
        headers = super().set_headers_to_response()
        if not self.user_id:
            headers.update({
                'HX-Reswap': 'innerHTML',
                'HX-Retarget': f'#record-error{self.record_id}'})
        return headers

    def get_attr_from_request(self):
        attr = {
            'record_id': 'pk',
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.record:
            context['record'] = self.record
        return context


record_sign_up = RecordSignUp.as_view()


class RecordCancel(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'records/record_cancel.html'
    response_htmx = True
    record = None

    def put(self, *args, **kwargs):
        self.user_id = self.get_or_set_user_id_from_cache()
        self.set_class_attributes_from_request()
        self.record = cancel_recording(user_id=self.user_id,
                                       record_id=self.record_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'record_id': 'pk',
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


class RecordsListUser(CustomMixin, TemplateResponseMixin, ContextMixin, View):

    template_name = 'records/htmx/user_records.html'
    user_records = None
    filter_form = None
    params = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()

        self.user_records, self.filter_form, self.params = get_user_records_from_db(
                                                                user_id=self.user_id,
                                                                event_id=self.event_id,
                                                                data=self.request.GET)

        self.page_obj, self.elided_page_range = self.create_pagination(object_list=self.user_records)

        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'user_id': 'user_pk',
            'event_id': 'event_pk'
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.user_records:
            context.update({
                'user_records': self.page_obj.object_list,
                'filter_form': self.filter_form,
                'params': self.params,
                'page_obj': self.page_obj,
                'elided_page_range': self.elided_page_range,
            })

        if self.user_id:
            context['user_pk'] = self.user_id
        if self.event_id:
            context['event_pk'] = self.event_id
        return context


records_user = RecordsListUser.as_view()


class RecordsDeleteAllUser(CustomMixin, TemplateResponseMixin, View):

    def delete(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        delete_event_and_all_records_user_from_db(user_id=self.user_id,
                                                  event_id=self.event_id)
        return HttpResponse(status=200)

    def get_attr_from_request(self):
        attr = {
            'event_id': 'event_pk',
            'user_id': 'user_pk',
        }
        return attr


delete_all_records_user = RecordsDeleteAllUser.as_view()


class EventRecordsUser(CustomMixin, TemplateResponseMixin, ContextMixin, View):

    template_name = 'records/htmx/user_event_records.html'
    user_event_records = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.user_event_records = get_user_event_records_from_db(user_id=self.user_id,
                                                                 event_id=self.event_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'user_id': 'user_pk',
            'event_id': 'event_pk'
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.user_event_records:
            context['user_event_records'] = self.user_event_records
        if self.user_id:
            context['user_pk'] = self.user_id
        return context


event_records_user = EventRecordsUser.as_view()


class RecordDeleteUser(CustomMixin, TemplateResponseMixin, ContextMixin, View):

    def delete(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        delete_recording_user_form_profile(record_id=self.record_id,
                                           user_id=self.user_id)

        return HttpResponse(status=200)

    def get_attr_from_request(self):
        attr = {
            'record_id': 'pk',
            'user_id': 'user_pk',
            'event_id': 'event_pk'
        }
        return attr


record_user_delete = RecordDeleteUser.as_view()
