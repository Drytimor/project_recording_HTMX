from django.db.models.query import QuerySet
from crispy_forms.utils import render_crispy_form
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import reverse, redirect, render
from django.template.context_processors import csrf
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views.generic.edit import FormMixin, Form, ContextMixin, TemplateResponseMixin, View
from django.contrib import messages

from organization.forms import (
    CreateOrganizationForm, UpdateOrganizationForm, CreateEmployeeForm, UpdateEmployeeForm,
    CreateEventForm, UpdateEventForm, CreateRecordForm, UpdateRecordForm)

from organization.mixins import CustomMixin, CustomTemplateResponseMixin
from organization.models import Employees, Events, Records, Organizations

from organization.services import (
    create_organization_from_db, delete_organization_from_db, update_organization_in_db, create_employee_in_db,
    update_employee_in_db, delete_employee_from_db, create_event_in_db, update_event_in_db, delete_event_from_db,
    create_record_in_db, delete_record_from_db, update_record_in_db, get_user_organization, get_organization_object,
    get_organization_employees_list, get_employees_object, get_organization_events, get_event_for_change,
    get_event_profile, get_event_and_event_records_for_organization_profile, get_record_object,
)

from organization.selectors import OrganizationEventsFilter


# CRUD Organization
class CreateOrganization(CustomTemplateResponseMixin, FormMixin, View):

    form_class = CreateOrganizationForm
    template_name = 'organizations/organization_create.html'
    form: 'Form'

    def get(self, *args, **kwargs):
        self.template_name = 'organizations/organization_create_form.html'
        self.form = self.get_form()
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def post(self, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        organization = create_organization_from_db(
            session_key_user=self.request.session.session_key,
            user=self.request.user,
            cleaned_data=form.cleaned_data
        )
        context = self.get_context_data(organization=organization)
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        if self.request.method == 'GET':
            kwargs['form'] = self.form
        return super(FormMixin, self).get_context_data(**kwargs)


organization_create = CreateOrganization.as_view()


class OrganizationProfile(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'organizations/organization_profile.html'
    response_htmx = True

    def get(self, *args, **kwargs):
        organization = get_user_organization(
            user_session_key=self.request.session.session_key,
            user=self.request.user
        )
        if organization is None:
            messages.add_message(
                request=self.request,
                level=messages.ERROR,
                message='Создайте организацию'
            )
        context = self.get_context_data(organization=organization)
        return self.render_to_response(context=context)


organization_profile = OrganizationProfile.as_view()


class OrganizationUpdate(CustomMixin, TemplateResponseMixin, FormMixin, View):

    template_name = 'organizations/organization_update.html'
    form_class = UpdateOrganizationForm
    form: 'Form'
    organization: 'Organizations'

    def get(self, *args, **kwargs):
        self.organization_id = self.kwargs.get('org_pk')
        self.template_name = 'organizations/organization_update_form.html'
        self.organization = get_organization_object(
            organization_id=self.organization_id
        )
        self.form = self.get_form()
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def post(self, *args, **kwargs):
        self.organization = get_organization_object(
            organization_id=self.kwargs.get('org_pk')
        )
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        update_organization_in_db(
            organization=self.organization,
            cleaned_data=form.cleaned_data
        )
        context = self.get_context_data( organization=self.organization)
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.organization
        return kwargs

    def get_context_data(self, **kwargs):
        if self.request.method == 'GET':
            kwargs['form'] = self.form
        return super(FormMixin, self).get_context_data(**kwargs)

    def delete(self, *args, **kwargs):
        self.organization_id = self.kwargs.get('org_pk')
        self.template_name = 'organizations/organization_delete.html',
        delete_organization_from_db(
            organization_id=self.organization_id,
            session_key_user=self.request.session.session_key,
            user=self.request.user
        )
        response = TemplateResponse(
            request=self.request,
            status=200,
            template=self.template_name,
            headers={
                'HX-Replace-Url': reverse('organization_profile')
            })
        return response


organization_update = OrganizationUpdate.as_view()


# CRUD Employee
class EmployeeCreate(TemplateResponseMixin, FormMixin, View):

    template_name = 'employees/employee_create.html'
    form_class = CreateEmployeeForm
    form: 'Form'
    employee: 'Employees'
    organization_id: int

    def get(self, *args, **kwargs):
        self.organization_id = self.kwargs.get('org_pk')
        self.template_name = 'employees/employee_create_form.html'
        self.form = self.get_form()
        context = self.get_context_data()
        return self.render_to_response(
            context=context,
            headers={
                'HX-Trigger-After-Swap': 'disabledBtnFormEmp'
            })

    def post(self, *args, **kwargs):
        self.organization_id = self.kwargs.get('org_pk')
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.employee = create_employee_in_db(
            organization_id=self.organization_id,
            cleaned_data=form.cleaned_data
        )
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
        if self.request.method == 'GET':
            kwargs['form'] = self.form
        if self.request.method == 'POST':
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


class EmployeesList(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'employees/employee_list.html'
    response_htmx = True
    employees_list: QuerySet['Employees']

    def get(self, *args, **kwargs):
        self.employees_list, self.organization_id = (
            get_organization_employees_list(
                user_session_key=self.request.session.session_key,
                user=self.request.user,
                data=self.request.GET)
        )
        if self.organization_id:
            self.page_obj, self.elided_page_range = (
                self.create_pagination(object_list=self.employees_list)
            )
            self.current_page_number = self.page_obj.number
        else:
            messages.add_message(
                request=self.request,
                level=messages.ERROR,
                message='Перейдите в профиль и создайте организацию.',
                extra_tags={
                    'url': reverse_lazy('organization_profile')
                }
            )
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        kwargs['organization_id'] = self.organization_id
        if self.page_obj:
            kwargs.update({
                'employees': self.page_obj.object_list,
                'page_obj': self.page_obj,
                'elided_page_range': self.elided_page_range,
                'page_number': self.current_page_number
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
            self.kwargs.get('emp_pk'), self.kwargs.get('org_pk')
        )
        self.employee = get_employees_object(
            employee_id=self.employee_id
        )
        context = self.get_context_data()
        headers = self.set_headers_to_response()
        return self.render_to_response(context=context, headers=headers)

    def delete(self, *args, **kwargs):

        delete_employee_from_db(employee=self.kwargs.get('emp_pk'),
                                organization_id=self.kwargs.get('org_pk')
                                )
        return HttpResponse(
            status=200,
            headers={
                'HX-Replace-Url': reverse(viewname='org_employees_list',
                                          kwargs={
                                              'page': self.request.GET.get('page')
                                          })
            })

    def set_headers_to_response(self):
        if self.employee_id is None and self.organization_id is None:
            return {
                'HX-Trigger-After-Swap': 'closeFormEmp'
            }

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

    def get(self, *args, **kwargs):
        self.organization_id = self.kwargs.get('org_pk')
        self.template_name = 'employees/employee_update_form.html'
        self.employee = get_employees_object(
            employee_id=self.kwargs.get('emp_pk'))
        self.form = self.get_form()
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def post(self, *args, **kwargs):
        self.employee_id, self.organization_id = (
            self.kwargs.get('emp_pk'), self.kwargs.get('org_pk')
        )
        self.employee = get_employees_object(
            employee_id=self.employee_id
        )
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        update_employee_in_db(employee=self.employee,
                              organization_id=self.organization_id,
                              cleaned_data=form.cleaned_data
                              )
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        if self.request.method == 'GET':
            kwargs['form'] = self.form
        if self.request.method == 'POST':
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


# CRUD Event
class EventsCreate(CustomTemplateResponseMixin, FormMixin, View):

    template_name = 'events/event_create.html'
    form_class = CreateEventForm
    event: 'Events'
    organization_id: int

    def get(self, *args, **kwargs):
        self.organization_id = self.kwargs.get('org_pk')
        self.template_name = 'events/event_create_form.html'
        self.form = self.get_form()
        context = self.get_context_data()
        return self.render_to_response(
            context=context,
            headers={
                'HX-Trigger-After-Swap': 'disabledBtnFormEvent'
            })

    def post(self, *args, **kwargs):
        self.organization_id = self.kwargs.get('org_pk')
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.event = create_event_in_db(
            organization_id=self.organization_id, cleaned_data=form.cleaned_data
        )
        context = self.get_context_data()
        return self.render_to_response(
            context=context,
            headers={
                 'HX-Trigger-After-Swap': 'activateBtnFormEvent'
            })

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        if self.request.method == 'GET':
            kwargs['form'] = self.form
        if self.request.method == 'POST':
            kwargs.update({
                'event': self.event,
                'organization_id': self.organization_id
            })
        return super(FormMixin, self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'organization_id': self.organization_id
        }


events_create = EventsCreate.as_view()


class EventsList(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'events/event_list.html'
    response_htmx = True
    events_list: QuerySet['Events']
    filter_class = OrganizationEventsFilter

    def get(self, *args, **kwargs):
        self.events_list, self.filter_form, self.params, self.organization_id = (
            get_organization_events(
                user_session_key=self.request.session.session_key,
                user=self.request.user, data=self.request.GET)
        )
        if self.organization_id:
            self.page_obj, self.elided_page_range = self.create_pagination(
                object_list=self.events_list)
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
    event_employees: 'Employees'
    organization_id: int
    event_id: int

    def get(self, *args, event_pk=None, org_pk=None, **kwargs):
        self.event_id, self.organization_id = (
            self.kwargs.get('event_pk'), self.kwargs.get('org_pk')
        )
        self.event, self.event_employees = get_event_profile(event_id=self.event_id)
        headers = self.set_headers_to_response()
        context = self.get_context_data()
        return self.render_to_response(context=context, headers=headers)

    def delete(self, *args, **kwargs):
        delete_event_from_db(event_id=self.kwargs.get('event_pk'),
                             organization_id=self.kwargs.get('org_pk')
                             )
        return HttpResponse(status=200)

    def set_headers_to_response(self):
        if self.organization_id is None and self.event_id is None:
            return {
                'HX-Trigger-After-Swap': 'closeFormEvent'
            }

    def get_context_data(self, **kwargs):
        kwargs.update({
            'event': self.event,
            'event_employees': self.event_employees,
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
    form: 'Form'
    event: 'Events'
    organization_employees: QuerySet['Employees']
    event_employees: QuerySet['Employees']
    event_id: int
    organization_id: int

    def get(self, *args, **kwargs):
        self.template_name = 'events/event_update_form.html'
        self.event_id, self.organization_id = (
            self.kwargs.get('event_pk'), self.kwargs.get('org_pk')
        )
        self.event, self.organization_employees = get_event_for_change(
            event_id=self.event_id, organization_id=self.organization_id
        )
        self.form = self.get_form()
        context = self.get_context_data(form=self.form)
        return self.render_to_response(context=context)

    def post(self, *args, **kwargs):
        self.event_id, self.organization_id = (
            self.kwargs.get('event_pk'), self.kwargs.get('org_pk')
        )
        self.event, self.organization_employees = (
            get_event_for_change(
                event_id=self.event_id, organization_id=self.organization_id)
        )
        self.form = self.get_form()
        if self.form.is_valid():
            return self.form_valid(self.form)
        return self.form_invalid(self.form)

    def form_valid(self, form):
        self.event_employees = update_event_in_db(
            event=self.event,  cleaned_data=form.cleaned_data,
            organization_id=self.organization_id
        )
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        if self.request.method == 'GET':
            kwargs['form'] = self.form
        if self.request.method == 'POST':
            kwargs.update({
                'event': self.event,
                'event_employees': self.event_employees,
                'organization_id': self.organization_id
            })
        return super(FormMixin, self).get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.event
        return kwargs

    def get_initial(self):
        return {
            'organization_id': self.organization_id,
            'organization_employees': self.organization_employees
        }


events_update = EventsUpdate.as_view()


# CRUD Record
class RecordCreate(TemplateResponseMixin, FormMixin, View):

    template_name = 'records/record_create.html'
    form_class = CreateRecordForm
    record: 'Records'
    event_id: int

    def get(self, *args, **kwargs):
        self.template_name = 'records/record_create_form.html'
        self.form = self.get_form()
        context = self.get_context_data()
        return self.render_to_response(
            context=context,
            headers={
                  'HX-Trigger-After-Swap': 'disabledBtnFormRecord'
                })

    def post(self, *args, **kwargs):
        self.event_id = self.kwargs.get('event_pk')
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.record = create_record_in_db(
            event_id=self.event_id, cleaned_data=form.cleaned_data
        )
        context = self.get_context_data()
        return self.render_to_response(
            context=context,
            headers={
                   'HX-Trigger-After-Swap': 'activateBtnFormRecord'
                })

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        if self.request.method == 'GET':
            kwargs['form'] = self.form
        if self.request.method == 'POST':
            kwargs['record'] = self.record
        return super(FormMixin, self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'event_id': self.kwargs['event_pk']
        }


record_create = RecordCreate.as_view()


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

    def delete(self, *args, **kwargs):
        delete_record_from_db(record_id=self.record_id,
                              event_id=self.request.GET.get('event')
                              )
        return HttpResponse(status=200)

    def set_headers_to_response(self):
        if self.record_id is None:
            return {
                'HX-Trigger-After-Swap': 'closeFormRecord'
            }


record_profile = RecordProfile.as_view()


class RecordsList(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'records/record_list.html'
    response_htmx = True
    event: QuerySet['Events']
    event_records: QuerySet['Records']
    params: str
    filter_form = None

    def get(self, *args, **kwargs):
        self.event_id, self.organization_id = (
            self.kwargs.get('event_pk'), self.kwargs.get('org_pk')
        )
        self.event, self.event_records, self.filter_form, self.params = (
            get_event_and_event_records_for_organization_profile(
                event_id=self.event_id, data=self.request.GET)
        )
        self.page_obj, self.elided_page_range = self.create_pagination(object_list=self.event_records)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'organization_id': self.organization_id,
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

    def get(self, *args, **kwargs):
        self.record_id = self.kwargs.get('record_pk')
        self.template_name = 'records/record_update_form.html'
        self.record = get_record_object(record_id=self.record_id)
        self.form = self.get_form()
        context = self.get_context_data()
        return self.render_to_response(context=context)

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
                            event_id=self.request.GET.get('event')
                            )
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        if self.request.method == 'GET':
            kwargs['form'] = self.form
        if self.request.method == 'POST':
            kwargs['record'] = self.record
        return super(FormMixin, self).get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.record
        return kwargs

    def get_initial(self):
        return {
            'params': self.request.GET.urlencode()
        }


record_update = RecordUpdate.as_view()


