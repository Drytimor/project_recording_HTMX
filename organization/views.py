from crispy_forms.utils import render_crispy_form
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import reverse, redirect, render
from django.template.context_processors import csrf
from django.template.response import TemplateResponse
from django.views.generic import View, DetailView
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.edit import FormMixin, BaseDeleteView

from organization.forms import (CreateOrganizationForm, UpdateOrganizationForm, CreateEmployeeForm, UpdateEmployeeForm,
                                CreateEventForm, UpdateEventForm, CreateRecordForm, UpdateRecordForm)
from organization.mixins import CustomMixin, CustomTemplateResponseMixin
from organization.services import (create_organization_from_db, get_organization_from_db, delete_organization_from_db,
                                   update_organization_in_db, get_employees_from_db, create_employee_in_db,
                                   update_employee_in_db, delete_employee_from_db, create_event_in_db,
                                   update_event_in_db, get_events_from_db, delete_event_from_db,get_event_profile_from_db,
                                   create_record_in_db, get_record_from_db, delete_record_from_db, update_record_in_db,
                                   get_event_and_all_records_from_db_for_organization,
                                   )


# CRUD Organization
class CreateOrganization(CustomTemplateResponseMixin, FormMixin, View):

    form_class = CreateOrganizationForm
    template_name = 'organizations/organization_create.html'
    user = None
    organization = None

    def post(self, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.user = self.request.user
        self.organization = create_organization_from_db(user=self.user,
                                                        form=form)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def set_headers_to_response(self):
        headers = {
            'HX-Replace-Url': reverse('organization_profile',
                                      kwargs={
                                          'pk': self.user.pk
                                      })
        }
        return headers

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.organization:
            context['organization'] = self.organization
        return context


organization_create = CreateOrganization.as_view()


class OrganizationCreateForm(TemplateResponseMixin, FormMixin, View):

    template_name = 'organizations/organization_create_form.html'
    form_class = CreateOrganizationForm

    def get(self, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context=context)


form_create_organization = OrganizationCreateForm.as_view()


class OrganizationUpdateForm(CustomMixin, TemplateResponseMixin, FormMixin, View):

    template_name = 'organizations/organization_update_form.html'
    form_class = UpdateOrganizationForm
    organization = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.organization = get_organization_from_db(organization_id=self.organization_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'organization_id': 'pk'
        }
        return attr

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.organization:
            kwargs['instance'] = self.organization
        return kwargs


form_update_organization = OrganizationUpdateForm.as_view()


class OrganizationProfile(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'organizations/organization_profile.html'
    response_htmx = True
    organization = None
    organization_id = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.organization = get_organization_from_db(user_id=self.user_id)
        if self.organization:
            self.organization_id = self.organization.pk
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'user_id': 'pk'
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.organization:
            context['organization'] = self.organization
        if self.organization_id:
            context['organization_id'] = self.organization_id
        return context


organization_profile = OrganizationProfile.as_view()


class OrganizationUpdate(CustomMixin, TemplateResponseMixin, FormMixin, View):

    template_name = 'organizations/organization_update.html'
    form_class = UpdateOrganizationForm
    organization = None

    def post(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.organization = get_organization_from_db(organization_id=self.organization_id)
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_attr_from_request(self):
        attr = {
            'organization_id': 'pk'
        }
        return attr

    def form_valid(self, form):
        context = self.get_context_data()
        update_organization_in_db(self.organization, form)
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.organization:
            context['organization'] = self.organization
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.organization:
            kwargs['instance'] = self.organization
        return kwargs


organization_update = OrganizationUpdate.as_view()


class GetOrganization(CustomMixin, TemplateResponseMixin, ContextMixin, View):

    template_name = 'organizations/get_organization.html'
    organization = None

    def get(self, *args, pk=None, **kwargs):
        self.set_class_attributes_from_request()
        self.organization = get_organization_from_db(organization_id=self.organization_id)
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
        return context


get_organization = GetOrganization.as_view()


class OrganizationDelete(CustomMixin, View):

    template_name = 'organizations/organization_delete.html',

    def post(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        delete_organization_from_db(organization_id=self.organization_id)
        response = TemplateResponse(request=self.request,
                                    status=200,
                                    template=self.template_name,
                                    headers={
                                        'HX-Replace-Url': reverse('profile')
                                    })
        return response

    def get_attr_from_request(self):
        attr = {
            'organization_id': 'pk'
        }
        return attr


organization_delete = OrganizationDelete.as_view()


# CRUD Employee
class EmployeeCreate(CustomMixin, CustomTemplateResponseMixin, FormMixin, View):

    template_name = 'employees/employee_create.html'
    form_class = CreateEmployeeForm
    employee = None

    def post(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_attr_from_request(self):
        attr = {
            'organization_id': 'pk'
        }
        return attr

    def set_headers_to_response(self):
        headers = {
            'HX-Trigger-After-Swap': 'activateBtnFormEmp'
        }
        return headers

    def form_valid(self, form):
        self.employee = create_employee_in_db(self.organization_id, form)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.employee:
            context['employee'] = self.employee
        if self.organization_id:
            context['organization_id'] = self.organization_id
        return context

    def get_initial(self):
        initial = {
            'organization_id': self.organization_id
        }
        return initial


employee_create = EmployeeCreate.as_view()


class EmployeesCreateForm(CustomMixin, CustomTemplateResponseMixin, FormMixin, View):

    template_name = 'employees/employee_create_form.html'
    form_class = CreateEmployeeForm

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'organization_id': 'pk'
        }
        return attr

    def set_headers_to_response(self):
        headers = {
            'HX-Trigger-After-Swap': 'disabledBtnFormEmp'
        }
        return headers

    def get_initial(self):
        initial = {
            'organization_id': self.organization_id
        }
        return initial


form_create_employee = EmployeesCreateForm.as_view()


class EmployeesUpdateForm(CustomMixin, TemplateResponseMixin, FormMixin, View):

    template_name = 'employees/employee_update_form.html'
    form_class = UpdateEmployeeForm
    employee = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.employee = get_employees_from_db(employee_id=self.employee_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'organization_id': 'org_pk',
            'employee_id': 'pk'
        }
        return attr

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.employee:
            kwargs['instance'] = self.employee
        return kwargs

    def get_initial(self):
        initial = {
            'organization_id': self.organization_id
        }
        return initial


form_update_employee = EmployeesUpdateForm.as_view()


class EmployeesList(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'employees/employee_list.html'
    employees_list = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.employees_list = get_employees_from_db(organization_id=self.organization_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'organization_id': 'pk'
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.employees_list:
            context['employees'] = self.employees_list
        if self.organization_id:
            context['organization_id'] = self.organization_id
        return context


employees_list = EmployeesList.as_view()


class EmployeeProfile(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'employees/employee_profile.html'
    employee = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.employee = get_employees_from_db(employee_id=self.employee_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'organization_id': 'org_pk',
            'employee_id': 'pk',
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.employee:
            context['employee'] = self.employee
        if self.organization_id:
            context['organization_id'] = self.organization_id
        return context


employee_profile = EmployeeProfile.as_view()


class EmployeeUpdate(CustomMixin, TemplateResponseMixin, FormMixin, View):

    template_name = 'employees/employee_update.html'
    form_class = UpdateEmployeeForm
    employee = None

    def post(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.employee = get_employees_from_db(employee_id=self.employee_id)
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_attr_from_request(self):
        attr = {
            'organization_id': 'org_pk',
            'employee_id': 'pk'
        }
        return attr

    def form_valid(self, form):
        context = self.get_context_data()
        update_employee_in_db(employee_id=self.employee_id, form=form)
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.employee:
            context['employee'] = self.employee
        if self.organization_id:
            context['organization_id'] = self.organization_id
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.employee:
            kwargs['instance'] = self.employee
        return kwargs

    def get_initial(self):
        initial = {
            'organization_id': self.organization_id
        }
        return initial


employee_update = EmployeeUpdate.as_view()


class GetEmployee(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'employees/get_employee.html'
    employee = None

    def get(self, *args, pk=None, org_pk=None, **kwargs):
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

    def set_headers_to_response(self):
        headers = super().set_headers_to_response()
        if self.employee_id is None and self.organization_id is None:
            headers['HX-Trigger-After-Swap'] = 'closeFormEmp'
        return headers

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.employee:
            context['employee'] = self.employee
        if self.organization_id:
            context['organization_id'] = self.organization_id
        return context


get_employee = GetEmployee.as_view()


class EmployeeDelete(CustomMixin, View):

    def post(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        employee = get_employees_from_db(employee_id=self.employee_id)
        delete_employee_from_db(employee)
        return HttpResponse(status=200)

    def get_attr_from_request(self):
        attr = {
            'employee_id': 'pk'
        }
        return attr


employee_delete = EmployeeDelete.as_view()


# CRUD Event
class EventsCreate(CustomMixin, CustomTemplateResponseMixin, FormMixin, View):

    template_name = 'events/event_create.html'
    form_class = CreateEventForm
    event = None

    def post(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_attr_from_request(self):
        param = {
            'organization_id': 'pk'
        }
        return param

    def set_headers_to_response(self):
        headers = {
            'HX-Trigger-After-Swap': 'activateBtnFormEvent'
        }
        return headers

    def form_valid(self, form):
        self.event = create_event_in_db(self.organization_id, form)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.event:
            context['event'] = self.event
        if self.organization_id:
            context['organization_id'] = self.organization_id
        return context

    def get_initial(self):
        initial = {
            'organization_id': self.organization_id
        }
        return initial


events_create = EventsCreate.as_view()


class EventCreateForm(CustomMixin, CustomTemplateResponseMixin, FormMixin, View):

    template_name = 'events/event_create_form.html'
    form_class = CreateEventForm

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'organization_id': 'pk'
        }
        return attr

    def set_headers_to_response(self):
        headers = {
            'HX-Trigger-After-Swap': 'disabledBtnFormEvent'
        }
        return headers

    def get_initial(self):
        initial = {
            'organization_id': self.organization_id
        }
        return initial


form_create_event = EventCreateForm.as_view()


class EventUpdateForm(CustomMixin, TemplateResponseMixin, FormMixin, View):

    template_name = 'events/event_update_form.html'
    form_class = UpdateEventForm
    event = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.event = get_events_from_db(event_id=self.event_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'event_id': 'pk',
            'organization_id': 'org_pk'
        }
        return attr

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.event:
            kwargs['instance'] = self.event
        return kwargs

    def get_initial(self):
        initial = {
            'organization_id': self.organization_id
        }
        return initial


form_update_event = EventUpdateForm.as_view()


class EventsList(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'events/event_list.html'
    response_htmx = True
    events_list = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.events_list = get_events_from_db(organization_id=self.organization_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'organization_id': 'pk'
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.events_list:
            context['events'] = self.events_list
        if self.organization_id:
            context['organization_id'] = self.organization_id
        return context


events_list = EventsList.as_view()


class EventProfile(CustomMixin, CustomTemplateResponseMixin, FormMixin, View):

    template_name = 'events/event_profile.html'
    response_htmx = True
    form_class = CreateRecordForm
    event = None
    records = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.event = get_event_profile_from_db(event_id=self.event_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'organization_id': 'org_pk',
            'event_id': 'pk'
        }
        return attr

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.event:
            context['event'] = self.event
        if self.event_id:
            context['event_id'] = self.event_id
        if self.organization_id:
            context['organization_id'] = self.organization_id
        return context

    def get_initial(self):
        initial = {
            'event_id': self.kwargs['pk']
        }
        return initial


event_profile = EventProfile.as_view()


class EventsUpdate(CustomMixin, TemplateResponseMixin, FormMixin, View):

    template_name = 'events/event_update.html'
    form_class = UpdateEventForm
    event = None
    event_profile = None

    def post(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.event = get_events_from_db(event_id=self.event_id)
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_attr_from_request(self):
        attr = {
            'event_id': 'pk',
            'organization_id': 'org_pk'
        }
        return attr

    def form_valid(self, form):
        update_event_in_db(self.event, form)
        self.event_profile = get_event_profile_from_db(event_id=self.event_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.event_profile:
            context['event'] = self.event_profile
        if self.organization_id:
            context['organization_id'] = self.organization_id
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.event:
            kwargs['instance'] = self.event
        return kwargs

    def get_initial(self):
        initial = {
            'organization_id': self.organization_id
        }
        return initial


events_update = EventsUpdate.as_view()


class GetEvent(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'events/get_event.html'
    event = None

    def get(self, *args, pk=None, org_pk=None, **kwargs):
        self.set_class_attributes_from_request()
        self.event = get_event_profile_from_db(event_id=self.event_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'event_id': 'pk',
            'organization_id': 'org_pk'
        }
        return attr

    def set_headers_to_response(self):
        headers = super().set_headers_to_response()
        if self.organization_id is None and self.employee_id is None:
            headers['HX-Trigger-After-Swap'] = 'closeFormEvent'
        return headers

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.event:
            context['event'] = self.event
        if self.organization_id:
            context['organization_id'] = self.organization_id
        return context


get_event = GetEvent.as_view()


class EventsDelete(CustomMixin, View):

    def post(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        event = get_events_from_db(event_id=self.event_id)
        delete_event_from_db(event)
        return HttpResponse(status=200)

    def get_attr_from_request(self):
        attr = {
            'event_id': 'pk'
        }
        return attr


events_delete = EventsDelete.as_view()


# CRUD Record
class RecordCreate(CustomMixin, CustomTemplateResponseMixin, FormMixin, View):

    template_name = 'records/record_create.html'
    form_class = CreateRecordForm
    event = None
    record = None

    def post(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_attr_from_request(self):
        attr = {
            'event_id': 'pk'
        }
        return attr

    def set_headers_to_response(self):
        headers = {
            'HX-Trigger-After-Swap': 'activateBtnFormRecord'
        }
        return headers

    def form_valid(self, form):
        self.record = create_record_in_db(self.event_id, form)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.record:
            context['record'] = self.record
        return context

    def get_initial(self):
        initial = {
            'event_id': self.kwargs['pk']
        }
        return initial


record_create = RecordCreate.as_view()


class RecordCreateForm(CustomMixin, CustomTemplateResponseMixin, FormMixin, View):

    template_name = 'records/record_create_form.html'
    form_class = CreateRecordForm

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'event_id': 'pk'
        }
        return attr

    def set_headers_to_response(self):
        headers = {
            'HX-Trigger-After-Swap': 'disabledBtnFormRecord'
        }
        return headers

    def get_initial(self):
        initial = {
            'event_id': self.event_id
        }
        return initial


form_create_record = RecordCreateForm.as_view()


class GetRecord(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'records/record_profile.html'
    record = None

    def get(self, *args, pk=None, **kwargs):
        self.set_class_attributes_from_request()
        self.record = get_record_from_db(record_id=self.record_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'record_id': 'pk'
        }
        return attr

    def set_headers_to_response(self):
        headers = super().set_headers_to_response()
        if self.record_id is None:
            headers['HX-Trigger-After-Swap'] = 'closeFormRecord'
        return headers

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.record:
            context['record'] = self.record
        return context


get_record = GetRecord.as_view()


class RecordUpdateForm(CustomMixin, TemplateResponseMixin, FormMixin, View):

    template_name = 'records/record_update_form.html'
    form_class = UpdateRecordForm
    record = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.record = get_record_from_db(record_id=self.record_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_attr_from_request(self):
        attr = {
            'record_id': 'pk'
        }
        return attr

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.record_id:
            kwargs['instance'] = self.record
        return kwargs


form_update_record = RecordUpdateForm.as_view()


class RecordsList(CustomMixin, CustomTemplateResponseMixin, ContextMixin, View):

    template_name = 'records/record_list.html'
    response_htmx = True
    records = None
    event = None
    employees = None

    def get(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.event, self.employees, self.records = get_event_and_all_records_from_db_for_organization(event_id=self.event_id)
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
        if self.records:
            context['records'] = self.records
        if self.event_id:
            context['event_id'] = self.event_id
        if self.organization_id:
            context['organization_id'] = self.organization_id
        if self.event:
            context['event'] = self.event
        if self.employees:
            context['employees'] = self.employees
        return context


records_list = RecordsList.as_view()


class RecordUpdate(CustomMixin, TemplateResponseMixin, FormMixin, View):

    template_name = 'records/record_update.html'
    form_class = UpdateRecordForm
    record = None

    def post(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        self.record = get_record_from_db(record_id=self.record_id)
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_attr_from_request(self):
        attr = {
            'record_id': 'pk'
        }
        return attr

    def form_valid(self, form):
        context = self.get_context_data()
        update_record_in_db(record_id=self.record_id, form=form)
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.record:
            context['record'] = self.record
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.record:
            kwargs['instance'] = self.record
        return kwargs


record_update = RecordUpdate.as_view()


class RecordDelete(CustomMixin, TemplateResponseMixin, FormMixin, View):

    def post(self, *args, **kwargs):
        self.set_class_attributes_from_request()
        delete_record_from_db(record_id=self.record_id)
        return HttpResponse(status=200)

    def get_attr_from_request(self):
        attr = {
            'record_id': 'pk'
        }
        return attr


record_delete = RecordDelete.as_view()

