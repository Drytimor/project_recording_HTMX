from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View, ContextMixin, TemplateResponseMixin
from django.contrib import messages
from customer.services import (
    get_organization_info, get_event_card, sign_up_for_event, cancel_recording,
    delete_recording_user_form_profile, get_user_events, get_event_and_event_records_for_customer,
    get_organization_events, set_assigned_event_to_user, delete_assigned_event_from_db,
    delete_event_and_all_records_user_from_db, get_event_records_for_user_profile,
    get_organizations_all, get_events_all, get_organization_employees, get_user_records_in_event,
    )

from organization.mixins import CustomTemplateResponseMixin, CustomMixin
from organization.services import get_employees_object


# CRUD organization
class OrganizationsAll(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'organizations/organization_all.html'
    response_htmx = True
    organizations = None
    filter_form = None
    params = None

    def get(self, *args, **kwargs):
        self.organizations, self.filter_form, self.params = (
            get_organizations_all(data=self.request.GET)
        )
        self.page_obj, self.elided_page_range = self.create_pagination(object_list=self.organizations)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'organizations': self.page_obj.object_list,
            'params': self.params,
            'page_obj': self.page_obj,
            'elided_page_range': self.elided_page_range,
            'filter_form': self.filter_form
        })
        return super().get_context_data(**kwargs)


organizations_all = OrganizationsAll.as_view()


class OrganizationInfo(CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'organizations/organization_info.html'
    response_htmx = True
    organization = None

    def get(self, *args, **kwargs):
        self.organization_id = self.kwargs.get('org_pk')
        self.organization = get_organization_info(organization_id=self.organization_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'organization': self.organization,
            'organization_id': self.organization_id
        })
        return super().get_context_data(**kwargs)


organization_info = OrganizationInfo.as_view()


class OrganizationEvents(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'events/org_events.html'
    response_htmx = True
    events = None
    filter_form = None
    params = None

    def get(self, *args, **kwargs):
        self.organization_id = self.kwargs.get('org_pk')
        self.events, self.filter_form, self.params = (
            get_organization_events(
                organization_id=self.organization_id, data=self.request.GET
            )
        )
        self.page_obj, self.elided_page_range = self.create_pagination(object_list=self.events)

        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'events': self.page_obj.object_list,
            'params': self.params,
            'page_obj': self.page_obj,
            'elided_page_range': self.elided_page_range,
            'organization_id': self.organization_id,
            'filter_form': self.filter_form,
        })
        return super().get_context_data(**kwargs)


organization_events = OrganizationEvents.as_view()


class OrganizationEmployees(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'employees/org_employees.html'
    response_htmx = True
    employees = None

    def get(self, *args, **kwargs):
        self.organization_id = self.kwargs.get('org_pk')
        self.employees = get_organization_employees(organization_id=self.organization_id)
        self.page_obj, self.elided_page_range = self.create_pagination(object_list=self.employees)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'employees': self.page_obj.object_list,
            'page_obj': self.page_obj,
            'elided_page_range': self.elided_page_range,
            'organization_id': self.organization_id
        })
        return super().get_context_data(**kwargs)


organization_employees = OrganizationEmployees.as_view()


# CRUD Employees
class EmployeeInfo(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'employees/employee_info.html'
    response_htmx = True
    employee = None

    def get(self, *args, **kwargs):
        self.employee_id, self.organization_id = (
            self.kwargs.get('emp_pk'), self.kwargs.get('org_pk')
        )
        self.employee = get_employees_object(employee_id=self.employee_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'employee': self.employee,
            'organization_id': self.organization_id
        })
        return super().get_context_data(**kwargs)


employee_info = EmployeeInfo.as_view()


# CRUD Event
class EventsAll(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'events/events_all.html'
    response_htmx = True
    events = None
    filter_form = None
    params = None

    def get(self, *args, **kwargs):
        self.events, self.filter_form, self.params, self.user_id = (
            get_events_all(
                user=self.request.user, data=self.request.GET,
                user_session_key=self.request.session.session_key
            )
        )
        self.page_obj, self.elided_page_range = self.create_pagination(object_list=self.events)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'events': self.page_obj.object_list,
            'user_pk': self.user_id,
            'params': self.params,
            'page_obj': self.page_obj,
            'elided_page_range': self.elided_page_range,
            'filter_form': self.filter_form
        })
        return super().get_context_data(**kwargs)


events_all = EventsAll.as_view()


class AssignedEvents(CustomMixin, TemplateResponseMixin, ContextMixin, View):

    template_name = 'events/htmx/assigned_event.html'
    assigned_event = None
    deleted_event = None

    def put(self, *args, **kwargs):
        self.event_id = self.kwargs.get('event_pk')
        self.assigned_event, self.user_id = set_assigned_event_to_user(
            user_session_key=self.request.session.session_key,
            user=self.request.user, event_id=self.event_id
        )
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def delete(self, *args, **kwargs):
        self.event_id = self.kwargs.get('event_pk')
        self.deleted_event = delete_assigned_event_from_db(
            user_session_key=self.request.session.session_key,
            user=self.request.user, event_id=self.event_id
        )
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'assigned_event': self.assigned_event,
            'deleted_event': self.deleted_event,
            'user_pk': self.user_id,
            'event_pk': self.event_id
        })
        return super().get_context_data(**kwargs)


assigned_events = AssignedEvents.as_view()


class EventsListUser(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'events/user_events.html'
    response_htmx = True
    user_events = None
    params = None
    filter_form = None

    def get(self, *args, **kwargs):
        self.user_events, self.filter_form, self.params, self.user_id = (
            get_user_events(
                user_session_key=self.request.session.session_key,
                user=self.request.user, data=self.request.GET)
        )
        self.page_obj, self.elided_page_range = self.create_pagination(object_list=self.user_events)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def delete(self, *args, **kwargs):
        self.event_id, self.user_id = (
            self.kwargs.get('event_pk'), self.kwargs.get('user_pk')
        )
        delete_event_and_all_records_user_from_db(user_id=self.user_id,
                                                  event_id=self.event_id)
        return HttpResponse(status=200)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'user_events': self.page_obj.object_list,
            'params': self.params,
            'page_obj': self.page_obj,
            'elided_page_range': self.elided_page_range,
            'filter_form': self.filter_form,
            'user_pk': self.user_id
        })
        return super().get_context_data(**kwargs)


events_user = EventsListUser.as_view()


class EventInfo(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'events/event_info.html'
    response_htmx = True
    event = None

    def get(self, *args, **kwargs):
        self.event_id, self.organization_id = (
            self.kwargs.get('event_pk'), self.kwargs.get('org_pk')
        )
        self.event = get_event_card(event_id=self.event_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'event': self.event,
            'organization_id': self.organization_id
        })
        return super().get_context_data(**kwargs)


event_info = EventInfo.as_view()


class EventRecords(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'records/event_records.html'
    response_htmx = True
    event = None
    params = None
    filter_form = None

    def get(self, *args, event_pk=None, org_pk=None, **kwargs):
        self.event_id, self.organization_id = (
            self.kwargs.get('event_pk'), self.kwargs.get('org_pk')
        )
        self.event, self.event_records, self.filter_form, self.params, self.user_id = (
            get_event_and_event_records_for_customer(
                user_session_key=self.request.session.session_key,
                user=self.request.user,
                data=self.request.GET,
                event_id=self.event_id)
        )
        self.page_obj, self.elided_page_range = self.create_pagination(object_list=self.event_records)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def put(self, *args, **kwargs):
        self.template_name = 'records/record_sign_up.html'
        self.record_id = self.request.GET.get('record_pk')
        self.record = sign_up_for_event(
            user_session_key=self.request.session.session_key,
            user=self.request.user, record_id=self.record_id
        )
        if self.record is None:
            messages.add_message(
                request=self.request,
                level=messages.ERROR,
                message='Ошибка'
            )
        context = self.get_context_data()
        headers = self.set_headers_to_response()
        return self.render_to_response(context=context, headers=headers)

    def set_headers_to_response(self):
        if self.record is None:
            return {
                'HX-Trigger': 'FailEntry',
                'HX-Reswap': 'none'
            }

    def get_context_data(self, **kwargs):
        match self.request.method:
            case 'GET':
                kwargs.update({
                    'event': self.event,
                    'records': self.page_obj.object_list,
                    'page_obj': self.page_obj,
                    'elided_page_range': self.elided_page_range,
                    'params': self.params,
                    'filter_form': self.filter_form,
                    'organization_id': self.organization_id,
                    'user_pk': self.user_id
                })
            case 'PUT':
                kwargs['record'] = self.record

        return super().get_context_data(**kwargs)


event_records = EventRecords.as_view()


# CRUD Records
class UserRecordsInEvent(CustomMixin, TemplateResponseMixin, ContextMixin, View):

    template_name = 'records/htmx/user_records.html'
    user_records_in_event = None
    filter_form = None
    params = None

    def get(self, *args, **kwargs):
        self.user_id, self.event_id = (
            self.kwargs.get('user_pk'), self.kwargs.get('event_pk')
        )
        self.user_records_in_event, self.filter_form, self.params = (
            get_user_records_in_event(user_id=self.user_id,
                                      event_id=self.event_id,
                                      data=self.request.GET)
        )
        self.page_obj, self.elided_page_range = self.create_pagination(object_list=self.user_records_in_event)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def delete(self, *args, **kwargs):
        self.record_id, self.user_id = (
            self.kwargs.get('record_pk'), self.kwargs.get('user_pk')
        )
        delete_recording_user_form_profile(record_id=self.record_id,
                                           user_id=self.user_id)

        return HttpResponse(status=200)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'user_records': self.page_obj.object_list,
            'filter_form': self.filter_form,
            'params': self.params,
            'page_obj': self.page_obj,
            'elided_page_range': self.elided_page_range,
            'user_pk': self.user_id,
            'event_pk': self.event_id
        })
        return super().get_context_data(**kwargs)


user_records_in_event = UserRecordsInEvent.as_view()


class RecordsEventForUserProfile(CustomMixin, TemplateResponseMixin, ContextMixin, View):

    template_name = 'records/htmx/user_event_records.html'
    records_event_in_user_profile = None
    params = None
    filter_form = None

    def get(self, *args, **kwargs):
        self.user_id, self.event_id = (
            self.kwargs.get('user_pk'), self.kwargs.get('event_pk')
        )
        self.records_event_in_user_profile, self.filter_form, self.params = (
            get_event_records_for_user_profile(
                user_id=self.user_id,
                event_id=self.event_id,
                data=self.request.GET)
        )
        self.page_obj, self.elided_page_range = self.create_pagination(object_list=self.records_event_in_user_profile)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def delete(self, *args, **kwargs):
        self.template_name = 'records/record_cancel.html'
        self.record_id = self.request.GET.get('record_pk')
        self.record, self.user_id = cancel_recording(
            user_session_key=self.request.session.session_key,
            user=self.request.user,
            record_id=self.record_id
        )
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        match self.request.method:
            case 'GET':
                kwargs.update({
                    'records_event': self.page_obj.object_list,
                    'filter_form': self.filter_form,
                    'params': self.params,
                    'page_obj': self.page_obj,
                    'elided_page_range': self.elided_page_range,
                    'user_pk': self.user_id,
                    'event_pk': self.event_id
                })
            case 'DELETE':
                kwargs.update({
                    'record': self.record,
                    'user_pk': self.user_id
                })
        return super().get_context_data(**kwargs)


records_event_for_user = RecordsEventForUserProfile.as_view()
