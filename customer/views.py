from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View, ContextMixin, TemplateResponseMixin

from customer.filters import RecordsListUserFilter, EventRecordsListFilter
from customer.services import (
    get_organization_info_from_db,
    get_event_card_from_db, sign_up_for_event, cancel_recording, get_user_records_from_db,
    delete_recording_user_form_profile, get_user_events_from_db, get_event_and_all_records_from_db_for_customer,
    get_user_event_records_from_db, assigned_event_to_user, delete_assigned_event_from_db,
    delete_event_and_all_records_user_from_db, get_all_events_using_filter,
    get_all_organization_using_filter, get_events_organizations_from_db)

from organization.mixins import CustomTemplateResponseMixin, CustomMixin
from organization.services import (get_employees_object, get_user_id_from_cache_or_db, get_filtered_event_records)
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
        kwargs.update({
            'organizations': self.page_obj.object_list,
            'params': self.params,
            'page_obj': self.page_obj,
            'elided_page_range': self.elided_page_range,
            'filter_form': self.filter_form
        })
        return super().get_context_data(**kwargs)


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

    def set_class_attributes_from_kwargs_request(self):
        return {
            'organization_id': 'pk'
        }

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
        self.set_class_attributes_from_request()
        self.events, self.filter_form, self.params = get_events_organizations_from_db(
                                                            organization_id=self.organization_id,
                                                            data=self.request.GET)

        self.page_obj, self.elided_page_range = self.create_pagination(object_list=self.events)

        context = self.get_context_data()
        return self.render_to_response(context=context)

    def set_class_attributes_from_kwargs_request(self):
        return {
            'organization_id': 'org_pk'
        }

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
        self.set_class_attributes_from_request()
        self.employees = get_employees_object(organization_id=self.organization_id)
        self.page_obj, self.elided_page_range = self.create_pagination(object_list=self.employees)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def set_class_attributes_from_kwargs_request(self):
        return {
            'organization_id': 'org_pk'
        }

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
        self.set_class_attributes_from_request()
        self.employee = get_employees_object(employee_id=self.employee_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def set_class_attributes_from_kwargs_request(self):
        return {
            'employee_id': 'pk',
            'organization_id': 'org_pk'
        }

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

        self.user_id = get_user_id_from_cache_or_db(
                            session_key_for_cache=self.request.session.session_key,
                            user=self.request.user)

        self.events, self.filter_form, self.params = get_all_events_using_filter(
                                                        user_id=self.user_id,
                                                        data=self.request.GET)

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

        self.user_id = get_user_id_from_cache_or_db(
                            session_key_for_cache=self.request.session.session_key,
                            user=self.request.user)

        self.set_class_attributes_from_request()

        self.assigned_event = assigned_event_to_user(user_id=self.user_id,
                                                     event_id=self.event_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def delete(self, *args, **kwargs):

        self.user_id = get_user_id_from_cache_or_db(
                            session_key_for_cache=self.request.session.session_key,
                            user=self.request.user)

        self.set_class_attributes_from_request()

        self.deleted_event = delete_assigned_event_from_db(user_id=self.user_id,
                                                           event_id=self.event_id)
        context = self.get_context_data()

        return self.render_to_response(context=context)

    def set_class_attributes_from_kwargs_request(self):
        return {
            'event_id': 'event_pk'
        }

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

        self.user_id = get_user_id_from_cache_or_db(
                            session_key_for_cache=self.request.session.session_key,
                            user=self.request.user)

        self.user_events, self.filter_form, self.params = get_user_events_from_db(
                                                                user_id=self.user_id,
                                                                data=self.request.GET)

        self.page_obj, self.elided_page_range = self.create_pagination(object_list=self.user_events)
        context = self.get_context_data()
        return self.render_to_response(context=context)

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
        self.set_class_attributes_from_request()
        self.event = get_event_card_from_db(event_id=self.event_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def set_class_attributes_from_kwargs_request(self):
        return {
            'event_id': 'pk',
            'organization_id': 'org_pk'
        }

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
    filter_class = EventRecordsListFilter

    def get(self, *args, **kwargs):

        self.user_id = get_user_id_from_cache_or_db(
                            session_key_for_cache=self.request.session.session_key,
                            user=self.request.user)

        self.set_class_attributes_from_request()

        self.event, event_records = get_event_and_all_records_from_db_for_customer(
            user_id=self.user_id, event_id=self.event_id)

        filtered_records, filter_form, params = get_filtered_event_records(
            event_records=event_records, filter_class=self.filter_class,
            data=self.request.GET)

        self.page_obj, self.elided_page_range = self.create_pagination(object_list=filtered_records)

        context = self.get_context_data()
        return self.render_to_response(context=context)

    def set_class_attributes_from_kwargs_request(self):
        return {
            'event_id': 'event_pk',
            'organization_id': 'org_pk',
        }

    def get_context_data(self, **kwargs):
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
        return super().get_context_data(**kwargs)


event_records = EventRecords.as_view()


# CRUD Records
class RecordSignUp(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'records/record_sign_up.html'
    response_htmx = True
    record = None

    def put(self, *args, **kwargs):

        self.user_id = get_user_id_from_cache_or_db(
                            session_key_for_cache=self.request.session.session_key,
                            user=self.request.user)

        self.set_class_attributes_from_request()

        self.record = sign_up_for_event(user_id=self.user_id,
                                        record_id=self.record_id)

        context = self.get_context_data()
        headers = self.set_headers_to_response()

        return self.render_to_response(context=context,
                                       headers=headers)

    def set_headers_to_response(self):
        if not self.user_id:
            return {
                'HX-Reswap': 'innerHTML',
                'HX-Retarget': f'#record-error{self.record_id}'
            }

    def set_class_attributes_from_kwargs_request(self):
        return {
            'record_id': 'pk',
        }

    def get_context_data(self, **kwargs):
        kwargs['record'] = self.record
        return super().get_context_data(**kwargs)


record_sign_up = RecordSignUp.as_view()


class RecordCancel(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'records/record_cancel.html'
    response_htmx = True
    record = None

    def put(self, *args, **kwargs):

        self.user_id = get_user_id_from_cache_or_db(
                            session_key_for_cache=self.request.session.session_key,
                            user=self.request.user)

        self.set_class_attributes_from_request()

        self.record = cancel_recording(user_id=self.user_id,
                                       record_id=self.record_id)

        context = self.get_context_data()

        return self.render_to_response(context=context)

    def set_class_attributes_from_kwargs_request(self):
        return {
            'record_id': 'pk',
        }

    def get_context_data(self, **kwargs):
        kwargs.update({
            'record': self.record,
            'user_pk': self.user_id
        })
        return super().get_context_data(**kwargs)


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

    def set_class_attributes_from_kwargs_request(self):
        return {
            'user_id': 'user_pk',
            'event_id': 'event_pk'
        }

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


records_user = RecordsListUser.as_view()


class RecordsDeleteAllUser(CustomMixin, TemplateResponseMixin, View):

    def delete(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        delete_event_and_all_records_user_from_db(user_id=self.user_id,
                                                  event_id=self.event_id)
        return HttpResponse(status=200)

    def set_class_attributes_from_kwargs_request(self):
        return {
            'event_id': 'event_pk',
            'user_id': 'user_pk',
        }


delete_all_records_user = RecordsDeleteAllUser.as_view()


class EventRecordsUser(CustomMixin, TemplateResponseMixin, ContextMixin, View):

    template_name = 'records/htmx/user_event_records.html'
    user_event_records = None
    params = None
    filter_form = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.user_event_records, self.filter_form, self.params = get_user_event_records_from_db(
                                                                        user_id=self.user_id,
                                                                        event_id=self.event_id,
                                                                        data=self.request.GET)

        self.page_obj, self.elided_page_range = self.create_pagination(object_list=self.user_event_records)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def set_class_attributes_from_kwargs_request(self):
        attr = {
            'user_id': 'user_pk',
            'event_id': 'event_pk'
        }
        return attr

    def get_context_data(self, **kwargs):
        kwargs.update({
            'user_event_records': self.page_obj.object_list,
            'filter_form': self.filter_form,
            'params': self.params,
            'page_obj': self.page_obj,
            'elided_page_range': self.elided_page_range,
            'user_pk': self.user_id,
            'event_pk': self.event_id
        })
        return super().get_context_data(**kwargs)


event_records_user = EventRecordsUser.as_view()


class RecordDeleteUser(CustomMixin, TemplateResponseMixin, ContextMixin, View):

    def delete(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        delete_recording_user_form_profile(record_id=self.record_id,
                                           user_id=self.user_id)

        return HttpResponse(status=200)

    def set_class_attributes_from_kwargs_request(self):
        return {
            'record_id': 'pk',
            'user_id': 'user_pk',
            'event_id': 'event_pk'
        }


record_user_delete = RecordDeleteUser.as_view()
