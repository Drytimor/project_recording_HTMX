from django.db.models.query import QuerySet
from crispy_forms.utils import render_crispy_form
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import reverse, redirect, render
from django.template.context_processors import csrf
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views.generic.base import ContextMixin, TemplateResponseMixin, View
from django.views.generic.edit import FormMixin
from django.contrib import messages

from customer.filters import OrganizationRecordsFilter, OrganizationEventsFilter

from organization.forms import (
    CreateOrganizationForm, UpdateOrganizationForm, CreateEmployeeForm, UpdateEmployeeForm,
    CreateEventForm, UpdateEventForm, CreateRecordForm, UpdateRecordForm)

from organization.mixins import CustomMixin, CustomTemplateResponseMixin
from organization.models import Employees, Events, Records, Organizations

from organization.services import (
    create_organization_from_db, get_organization_object, delete_organization_from_db,
    update_organization_in_db, get_employees_object, create_employee_in_db, get_filtered_records,
    get_organization_employees_list, update_employee_in_db, delete_employee_from_db, create_event_in_db,
    get_organization_events, update_event_in_db, get_event_object, delete_event_from_db,
    get_filtered_organization_events, get_event_profile_from_db, create_record_in_db, get_record_object,
    delete_record_from_db, update_record_in_db, get_event_and_all_records_from_db_for_organization,
    get_user_organization_from_profile)


# CRUD Organization
class CreateOrganization(CustomTemplateResponseMixin, FormMixin, View):

    form_class = CreateOrganizationForm
    template_name = 'organizations/organization_create.html'

    def post(self, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        organization = create_organization_from_db(
            session_key_user=self.request.session.session_key,
            user=self.request.user,
            cleaned_data=form.cleaned_data)

        context = self.get_context_data(organization=organization)
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)


organization_create = CreateOrganization.as_view()


class OrganizationCreateForm(TemplateResponseMixin, FormMixin, View):

    template_name = 'organizations/organization_create_form.html'
    form_class = CreateOrganizationForm

    def get(self, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context=context)


form_create_organization = OrganizationCreateForm.as_view()


class OrganizationUpdateForm(TemplateResponseMixin, FormMixin, View):

    template_name = 'organizations/organization_update_form.html'
    form_class = UpdateOrganizationForm
    organization: 'Organizations'

    def get(self, *args, **kwargs):
        self.organization = get_organization_object(
            organization_id=self.kwargs.get('org_pk'))

        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.organization
        return kwargs


form_update_organization = OrganizationUpdateForm.as_view()


class OrganizationProfile(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'organizations/organization_profile.html'
    response_htmx = True

    def get(self, *args, **kwargs):
        organization = get_user_organization_from_profile(
            user_session_key=self.request.session.session_key,
            user=self.request.user)

        if organization is None:
            messages.add_message(
                request=self.request,
                level=messages.ERROR,
                message='Создайте организацию')

        context = self.get_context_data(
            organization=organization)

        return self.render_to_response(context=context)


organization_profile = OrganizationProfile.as_view()


class OrganizationUpdate(CustomMixin, TemplateResponseMixin, FormMixin, View):

    template_name = 'organizations/organization_update.html'
    form_class = UpdateOrganizationForm
    organization: 'Organizations'

    def post(self, *args, **kwargs):
        self.organization = get_organization_object(
            organization_id=self.kwargs.get('org_pk'))

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        update_organization_in_db(
            organization=self.organization,
            cleaned_data=form.cleaned_data)

        context = self.get_context_data(
            organization=self.organization)

        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.organization
        return kwargs


organization_update = OrganizationUpdate.as_view()


class OrganizationDelete(TemplateResponseMixin, View):

    template_name = 'organizations/organization_delete.html',

    def post(self, *args, **kwargs):

        delete_organization_from_db(
            organization_id=self.kwargs.get('org_pk'),
            session_key_user=self.request.session.session_key,
            user=self.request.user)

        response = TemplateResponse(
            request=self.request,
            status=200,
            template=self.template_name,
            headers={
                'HX-Replace-Url': reverse('organization_profile')
            })
        return response


organization_delete = OrganizationDelete.as_view()


# CRUD Employee
class EmployeeCreate(TemplateResponseMixin, FormMixin, View):

    template_name = 'employees/employee_create.html'
    form_class = CreateEmployeeForm
    employee: 'Employees'
    organization_id: int

    def post(self, *args, **kwargs):
        self.organization_id = self.kwargs.get('org_pk')
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.employee = create_employee_in_db(
            self.organization_id, cleaned_data=form.cleaned_data)

        context = self.get_context_data()
        return self.render_to_response(
            context=context,
            headers={
                'HX-Trigger-After-Swap': 'activateBtnFormEmp'
            })

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'employee': self.employee,
            'organization_id': self.organization_id
        })
        return super().get_context_data(**kwargs)

    def get_initial(self):
        return {
            'organization_id': self.organization_id
        }


employee_create = EmployeeCreate.as_view()


class EmployeesCreateForm(TemplateResponseMixin, FormMixin, View):

    template_name = 'employees/employee_create_form.html'
    form_class = CreateEmployeeForm

    def get(self, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(
            context=context,
            headers={
                'HX-Trigger-After-Swap': 'disabledBtnFormEmp'
            })

    def get_initial(self):
        return {
            'organization_id': self.kwargs.get('org_pk')
        }


form_create_employee = EmployeesCreateForm.as_view()


class EmployeesUpdateForm(CustomMixin, TemplateResponseMixin, FormMixin, View):

    template_name = 'employees/employee_update_form.html'
    form_class = UpdateEmployeeForm
    employee: 'Employees'

    def get(self, *args, **kwargs):
        self.employee = get_employees_object(
            employee_id=self.kwargs.get('emp_pk'))

        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.employee
        return kwargs

    def get_initial(self):
        return {
            'organization_id': self.kwargs.get('org_pk')
        }


form_update_employee = EmployeesUpdateForm.as_view()


class EmployeesList(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'employees/employee_list.html'
    response_htmx = True
    employees_list: QuerySet['Employees']

    def get(self, *args, **kwargs):
        self.employees_list, self.organization_id = get_organization_employees_list(
            session_key_user=self.request.session.session_key,
            user=self.request.user,
            data=self.request.GET)

        if self.organization_id:
            self.page_obj, self.elided_page_range = self.create_pagination(
                object_list=self.employees_list)

        else:
            messages.add_message(
                request=self.request,
                level=messages.ERROR,
                message='Перейдите в профиль и создайте организацию.',
                extra_tags={
                    'url': reverse_lazy('organization_profile')
                })

        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        kwargs['organization_id'] = self.organization_id

        if self.page_obj:
            kwargs.update({
                'employees': self.page_obj.object_list,
                'page_obj': self.page_obj,
                'elided_page_range': self.elided_page_range,
            })
        return super().get_context_data(**kwargs)


org_employees_list = EmployeesList.as_view()


class EmployeeProfile(CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'employees/employee_profile.html'
    response_htmx = True
    employee: 'Employees'
    employee_id: int
    organization_id: int

    def get(self, *args, emp_pk=None, org_pk=None, **kwargs):
        self.employee_id, self.organization_id = (
            self.kwargs.get('emp_pk'), self.kwargs.get('org_pk'))

        self.employee = get_employees_object(
            employee_id=self.employee_id)

        context = self.get_context_data()
        headers = self.set_headers_to_response()

        return self.render_to_response(
            context=context, headers=headers)

    def set_headers_to_response(self):
        headers = super().set_headers_to_response()
        if self.employee_id is None and self.organization_id is None:
            headers['HX-Trigger-After-Swap'] = 'closeFormEmp'
        return headers

    def get_context_data(self, **kwargs):
        kwargs.update({
            'employee': self.employee,
            'organization_id': self.organization_id
        })
        return super().get_context_data(**kwargs)


employee_profile = EmployeeProfile.as_view()


class EmployeeUpdate(CustomMixin, TemplateResponseMixin, FormMixin, View):

    template_name = 'employees/employee_update.html'
    form_class = UpdateEmployeeForm
    employee: 'Employees'

    def post(self, *args, **kwargs):
        self.employee_id, self.organization_id = (
            self.kwargs.get('emp_pk'), self.kwargs.get('org_pk'))

        self.employee = get_employees_object(
            employee_id=self.employee_id)

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        update_employee_in_db(employee=self.employee,
                              organization_id=self.organization_id,
                              cleaned_data=form.cleaned_data)

        context = self.get_context_data()
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'employee': self.employee,
            'organization_id': self.organization_id
        })
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.employee
        return kwargs

    def get_initial(self):
        return {
            'organization_id': self.organization_id
        }


employee_update = EmployeeUpdate.as_view()


class EmployeeDelete(View):

    def post(self, *args, **kwargs):

        delete_employee_from_db(employee=self.kwargs.get('emp_pk'),
                                organization_id=self.kwargs.get('org_pk'))

        return HttpResponse(status=200)


employee_delete = EmployeeDelete.as_view()


# CRUD Event
class EventsCreate(CustomTemplateResponseMixin, FormMixin, View):

    template_name = 'events/event_create.html'
    form_class = CreateEventForm
    event: 'Events'
    organization_id: int

    def post(self, *args, **kwargs):
        self.organization_id = self.kwargs.get('org_pk')
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.event = create_event_in_db(self.organization_id, cleaned_data=form.cleaned_data)
        context = self.get_context_data()
        return self.render_to_response(context=context,
                                       headers={
                                           'HX-Trigger-After-Swap': 'activateBtnFormEvent'
                                       })

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'event': self.event,
            'organization_id': self.organization_id
        })
        return super().get_context_data(**kwargs)

    def get_initial(self):
        return {
            'organization_id': self.organization_id
        }


events_create = EventsCreate.as_view()


class EventCreateForm(CustomMixin, CustomTemplateResponseMixin, FormMixin, View):

    template_name = 'events/event_create_form.html'
    form_class = CreateEventForm

    def get(self, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context=context,
                                       headers={
                                           'HX-Trigger-After-Swap': 'disabledBtnFormEvent'
                                       })

    def get_initial(self):
        return {
            'organization_id': self.kwargs.get('org_pk')
        }


form_create_event = EventCreateForm.as_view()


class EventUpdateForm(TemplateResponseMixin, FormMixin, View):

    template_name = 'events/event_update_form.html'
    form_class = UpdateEventForm
    event: 'Events'
    organization_id: int
    event_id: int

    def get(self, *args, **kwargs):
        self.event_id, self.organization_id = (
            self.kwargs.get('event_pk'), self.kwargs.get('org_pk'))

        self.event = get_event_object(event_id=self.event_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.event
        return kwargs

    def get_initial(self):
        return {
            'organization_id': self.organization_id
        }


form_update_event = EventUpdateForm.as_view()


class EventsList(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'events/event_list.html'
    response_htmx = True
    events_list: QuerySet['Events']
    filter_class = OrganizationEventsFilter

    def get(self, *args, **kwargs):
        self.events_list, self.organization_id = get_organization_events(
            session_key_user=self.request.session.session_key,
            user=self.request.user, data=self.request.GET)

        if self.organization_id:
            filtered_events_list, self.filter_form, self.params = get_filtered_organization_events(
                queryset=self.events_list, data=self.request.GET,
                filter_class=self.filter_class)

            self.page_obj, self.elided_page_range = self.create_pagination(
                object_list=filtered_events_list)
        else:
            messages.add_message(
                request=self.request,
                level=messages.ERROR,
                message='Перейдите в профиль и создайте организацию.',
                extra_tags={
                    'url': reverse_lazy('organization_profile')
                })

        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        kwargs['organization_id'] = self.organization_id
        if self.page_obj:
            kwargs.update({
                'events': self.page_obj.object_list,
                'page_obj': self.page_obj,
                'elided_page_range': self.elided_page_range,
                'params': self.params,
                'filter_form': self.filter_form
            })
        return super().get_context_data(**kwargs)


org_events_list = EventsList.as_view()


class EventProfile(CustomTemplateResponseMixin, FormMixin, View):

    template_name = 'events/event_profile.html'
    response_htmx = True
    form_class = CreateRecordForm
    event: 'Events'
    organization_id: int
    event_id: int

    def get(self, *args, event_pk=None, org_pk=None, **kwargs):
        self.event_id, self.organization_id = (
            self.kwargs.get('event_pk'), self.kwargs.get('org_pk'))

        self.event = get_event_profile_from_db(event_id=self.event_id)
        headers = self.set_headers_to_response()
        context = self.get_context_data()

        return self.render_to_response(context=context, headers=headers)

    def set_headers_to_response(self):
        headers = super().set_headers_to_response()
        if self.organization_id is None and self.event_id is None:
            headers['HX-Trigger-After-Swap'] = 'closeFormEvent'
        return headers

    def get_context_data(self, **kwargs):
        kwargs.update({
            'event': self.event,
            'event_id': self.event_id,
            'organization_id': self.organization_id
        })
        return super().get_context_data(**kwargs)

    def get_initial(self):
        return {
            'event_id': self.event_id
        }


event_profile = EventProfile.as_view()


class EventsUpdate(TemplateResponseMixin, FormMixin, View):

    template_name = 'events/event_update.html'
    form_class = UpdateEventForm
    event: 'Events'
    event_profile: 'Events'
    event_id: int
    organization_id: int

    def post(self, *args, **kwargs):
        self.event_id, self.organization_id = (
            self.kwargs.get('event_pk'), self.kwargs.get('org_pk'))

        self.event = get_event_object(event_id=self.event_id)
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        update_event_in_db(event=self.event,
                           cleaned_data=form.cleaned_data,
                           organization_id=self.organization_id)

        self.event_profile = get_event_profile_from_db(event_id=self.event_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'event': self.event_profile,
            'organization_id': self.organization_id
        })
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.event
        return kwargs

    def get_initial(self):
        return {
            'organization_id': self.organization_id
        }


events_update = EventsUpdate.as_view()


class GetEvent(CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'events/get_event.html'
    event: 'Events'
    event_id: int
    organization_id: int

    def get(self, *args, event_pk=None, org_pk=None, **kwargs):
        self.event_id, self.organization_id = (
            self.kwargs.get('event_pk'), self.kwargs.get('org_pk'))

        self.event = get_event_profile_from_db(event_id=self.event_id)
        context = self.get_context_data()
        headers = self.set_headers_to_response()

        return self.render_to_response(context=context,
                                       headers=headers)

    def set_headers_to_response(self):
        headers = super().set_headers_to_response()
        if self.organization_id is None and self.event_id is None:
            headers['HX-Trigger-After-Swap'] = 'closeFormEvent'
        return headers

    def get_context_data(self, **kwargs):
        kwargs.update({
            'event': self.event,
            'organization_id': self.organization_id
        })
        return super().get_context_data(**kwargs)


get_event = GetEvent.as_view()


class EventsDelete(View):

    def post(self, *args, **kwargs):

        delete_event_from_db(event_id=self.kwargs.get('event_pk'),
                             organization_id=self.kwargs.get('org_pk'))

        return HttpResponse(status=200)


events_delete = EventsDelete.as_view()


# CRUD Record
class RecordCreate(TemplateResponseMixin, FormMixin, View):

    template_name = 'records/record_create.html'
    form_class = CreateRecordForm
    record: 'Records'
    event_id: int

    def post(self, *args, **kwargs):
        self.event_id = self.kwargs.get('event_pk')
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.record = create_record_in_db(
            event_id=self.event_id, cleaned_data=form.cleaned_data)

        context = self.get_context_data()
        return self.render_to_response(context=context,
                                       headers={
                                           'HX-Trigger-After-Swap': 'activateBtnFormRecord'
                                        })

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        kwargs['record'] = self.record
        return super().get_context_data(**kwargs)

    def get_initial(self):
        return {
            'event_id': self.kwargs['event_pk']
        }


record_create = RecordCreate.as_view()


class RecordCreateForm(TemplateResponseMixin, FormMixin, View):

    template_name = 'records/record_create_form.html'
    form_class = CreateRecordForm

    def get(self, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context=context,
                                       headers={
                                           'HX-Trigger-After-Swap': 'disabledBtnFormRecord'
                                        })

    def get_initial(self):
        return {
            'event_id': self.kwargs.get('event_pk')
        }


form_create_record = RecordCreateForm.as_view()


class RecordProfile(CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'records/record_profile.html'
    record: 'Records'
    record_id: int

    def get(self, *args, pk=None, **kwargs):
        self.record_id = self.kwargs.get('record_pk')
        self.record = get_record_object(record_id=self.record_id)
        context = self.get_context_data(record=self.record)
        headers = self.set_headers_to_response()
        return self.render_to_response(context=context,
                                       headers=headers)

    def set_headers_to_response(self):
        headers = super().set_headers_to_response()
        if self.record_id is None:
            headers['HX-Trigger-After-Swap'] = 'closeFormRecord'
        return headers


record_profile = RecordProfile.as_view()


class RecordUpdateForm(TemplateResponseMixin, FormMixin, View):

    template_name = 'records/record_update_form.html'
    form_class = UpdateRecordForm
    record: 'Records'

    def get(self, *args, **kwargs):
        self.record = get_record_object(record_id=self.kwargs.get('record_pk'))
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.record
        return kwargs

    def get_initial(self):
        return {
            'params': self.request.GET.urlencode()
        }


form_update_record = RecordUpdateForm.as_view()


class RecordsList(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'records/record_list.html'
    response_htmx = True
    event: QuerySet['Events']
    event_records: QuerySet['Records']
    params: str
    filter_class = OrganizationRecordsFilter
    filter_form = None

    def get(self, *args, **kwargs):
        self.event_id, self.organization_id = (
            self.kwargs.get('event_pk'), self.kwargs.get('org_pk'))

        self.event, self.event_records = get_event_and_all_records_from_db_for_organization(
            event_id=self.event_id)

        filtered_event_records, self.filter_form, self.params = get_filtered_records(
            queryset=self.event_records, data=self.request.GET,
            filter_class=self.filter_class)

        self.page_obj, self.elided_page_range = self.create_pagination(object_list=filtered_event_records)

        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'organization_id': self.organization_id,
            'event_id': self.event_id,
            'event': self.event,
            'event_records': self.page_obj.object_list,
            'page_obj': self.page_obj,
            'elided_page_range': self.elided_page_range,
            'filter_form': self.filter_form,
            'params': self.params
        })
        return super().get_context_data(**kwargs)


org_records_list = RecordsList.as_view()


class RecordUpdate(TemplateResponseMixin, FormMixin, View):

    template_name = 'records/record_update.html'
    form_class = UpdateRecordForm
    record: 'Records'
    record_id: int

    def post(self, *args, **kwargs):
        self.record_id = self.kwargs.get('record_pk')
        self.record = get_record_object(record_id=self.record_id)
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        context = self.get_context_data()

        update_record_in_db(record_id=self.record_id,
                            cleaned_data=form.cleaned_data,
                            event_id=self.request.GET.get('event'))

        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        kwargs['record'] = self.record
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.record
        return kwargs

    def get_initial(self):
        return {
            'params': self.request.GET.urlencode()
        }


record_update = RecordUpdate.as_view()


class RecordDelete(TemplateResponseMixin, FormMixin, View):

    def post(self, *args, **kwargs):

        delete_record_from_db(record_id=self.kwargs.get('record_pk'),
                              event_id=self.request.GET.get('event'))

        return HttpResponse(status=200)


record_delete = RecordDelete.as_view()

