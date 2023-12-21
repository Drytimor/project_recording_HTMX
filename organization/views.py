from crispy_forms.utils import render_crispy_form
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import reverse, redirect, render
from django.template.context_processors import csrf
from django.views.generic import View
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.edit import FormMixin, BaseDeleteView

from organization.forms import CreateOrganizationForm, UpdateOrganizationForm, CreateEmployeeForm, UpdateEmployeeForm, \
    CreateEventForm, UpdateEventForm, CreateRecordForm
from organization.services import create_organization_from_db, get_organization_from_db, delete_organization_from_db, \
    update_organization_in_db, get_employees_from_db, create_employee_in_db, update_employee_in_db, \
    delete_employee_from_db, create_event_in_db, update_event_in_db, get_events_from_db, delete_event_from_db, \
    get_event_profile_from_db, create_record_in_db, get_records_from_db


# CRUD Organization
class CreateOrganization(TemplateResponseMixin, FormMixin, View):

    form_class = CreateOrganizationForm
    template_name = 'organizations/organization_create.html'
    user = None
    organization = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.organization:
            context['organization'] = self.organization
        return context

    def post(self, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.user = self.request.user
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.organization = create_organization_from_db(self.user, form)
        context = self.get_context_data()
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
    organization = None

    def get(self, *args, **kwargs):
        self.organization = self.get_organization_from_services()
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_organization_from_services(self):
        organization_id = self.kwargs['pk']
        organization = get_organization_from_db(organization_id=organization_id)
        return organization

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.organization:
            kwargs['instance'] = self.organization
        return kwargs


form_update_organization = OrganizationUpdateForm.as_view()


class OrganizationProfile(TemplateResponseMixin, ContextMixin, View):

    organization = None
    template_name = 'organizations/organization_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.organization:
            context['organization'] = self.organization
        return context

    def get_organization_from_services(self):
        user = self.request.user
        organization = get_organization_from_db(user=user)
        return organization

    def get(self, *args, **kwargs):
        self.organization = self.get_organization_from_services()
        context = self.get_context_data()
        return self.render_to_response(context=context)


organization_profile = OrganizationProfile.as_view()


class OrganizationUpdate(TemplateResponseMixin, FormMixin, View):

    template_name = 'organizations/organization_update.html'
    form_class = UpdateOrganizationForm
    organization = None

    def get_organization_from_services(self):
        organization_id = self.kwargs['pk']
        organization = get_organization_from_db(organization_id=organization_id)
        return organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.organization:
            context['organization'] = self.organization
        return context

    def post(self, *args, **kwargs):
        self.organization = self.get_organization_from_services()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        context = self.get_context_data()
        update_organization_in_db(self.organization, form)
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)


organization_update = OrganizationUpdate.as_view()


class OrganizationDelete(View):

    def post(self, *args, **kwargs):
        user = self.request.user
        delete_organization_from_db(user)
        return render(self.request, template_name='organizations/organization_delete.html')


organization_delete = OrganizationDelete.as_view()


# CRUD Employee
class EmployeeCreate(TemplateResponseMixin, FormMixin, View):

    template_name = 'employees/employee_create.html'
    form_class = CreateEmployeeForm
    organization_id = None
    employee = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.employee:
            context['employee'] = self.employee
        return context

    def get_organization_id_from_request(self):
        return self.kwargs['pk']

    def get_initial(self):
        initial = {
            'organization_id': self.organization_id
        }
        return initial

    def post(self, *args, **kwargs):
        self.organization_id = self.get_organization_id_from_request()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.employee = create_employee_in_db(self.organization_id, form)
        context = self.get_context_data()
        return self.render_to_response(context=context, headers={
            'HX-Trigger-After-Swap': 'ActivateBtnFormEmp'
        })

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)


employee_create = EmployeeCreate.as_view()


class EmployeesCreateForm(TemplateResponseMixin, FormMixin, View):

    template_name = 'employees/employee_create_form.html'
    form_class = CreateEmployeeForm
    organization_id = None

    def get(self, *args, **kwargs):
        self.organization_id = self.kwargs['pk']
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_initial(self):
        initial = {
            'organization_id': self.organization_id
        }
        return initial


form_create_employee = EmployeesCreateForm.as_view()


class EmployeesUpdateForm(TemplateResponseMixin, FormMixin, View):

    template_name = 'employees/employee_update_form.html'
    form_class = UpdateEmployeeForm
    employee = None

    def get(self, *args, **kwargs):
        self.employee = self.get_employee_from_services()
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_employee_from_services(self):
        employee_id = self.kwargs['pk']
        employee = get_employees_from_db(employee_id=employee_id)
        return employee

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.employee:
            kwargs.update({"instance": self.employee})
        return kwargs


form_update_employee = EmployeesUpdateForm.as_view()


class EmployeesList(TemplateResponseMixin, ContextMixin, View):

    template_name = 'employees/employee_list.html'
    employees_list = None
    organization_id = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.employees_list:
            context['employees'] = self.employees_list
        if self.organization_id:
            context['organization_id'] = self.organization_id
        return context

    def get(self, *args, **kwargs):
        self.employees_list = self.get_employees_from_services()
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_employees_from_services(self):
        self.organization_id = self.kwargs['pk']
        employees = get_employees_from_db(organization_id=self.organization_id)
        return employees


employees_list = EmployeesList.as_view()


class EmployeeProfile(TemplateResponseMixin, ContextMixin, View):

    template_name = 'employees/employee_profile.html'
    employee = None

    def get(self, *args, **kwargs):
        employee_id = self.kwargs['pk']
        self.employee = get_employees_from_db(employee_id=employee_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.employee:
            context['employee'] = self.employee
        return context


employee_profile = EmployeeProfile.as_view()


class EmployeeUpdate(TemplateResponseMixin, FormMixin, View):

    template_name = 'employees/employee_update.html'
    form_class = UpdateEmployeeForm
    employee = None

    def get_employee_from_services(self):
        employee_id = self.kwargs['pk']
        employee = get_employees_from_db(employee_id=employee_id)
        return employee

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.employee:
            kwargs['instance'] = self.employee
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.employee:
            context['employee'] = self.employee
        return context

    def post(self, *args, **kwargs):
        self.employee = self.get_employee_from_services()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        context = self.get_context_data()
        update_employee_in_db(self.employee, form)
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)


employee_update = EmployeeUpdate.as_view()


class EmployeeDelete(View):

    def post(self, *args, **kwargs):
        employee_id = self.kwargs['pk']
        employee = get_employees_from_db(employee_id=employee_id)
        delete_employee_from_db(employee)
        return HttpResponse(status=200)


employee_delete = EmployeeDelete.as_view()


# CRUD Event
class EventsCreate(TemplateResponseMixin, FormMixin, View):

    template_name = 'events/event_create.html'
    form_class = CreateEventForm
    organization_id = None
    event = None

    def get_initial(self):
        initial = {
            'organization_id': self.get_organization_id_from_request()
        }
        return initial

    def get_organization_id_from_request(self):
        return self.kwargs['pk']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.event:
            context['event'] = self.event
        return context

    def post(self, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.organization_id = self.get_organization_id_from_request()
        self.event = create_event_in_db(self.organization_id, form)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)


events_create = EventsCreate.as_view()


class EventCreateForm(TemplateResponseMixin, FormMixin, View):

    template_name = 'events/event_create_form.html'
    form_class = CreateEventForm
    organization_id = None

    def get(self, *args, **kwargs):
        self.organization_id = self.kwargs['pk']
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_initial(self):
        initial = {
            'organization_id': self.organization_id
        }
        return initial


form_create_event = EventCreateForm.as_view()


class EventUpdateForm(TemplateResponseMixin, FormMixin, View):

    template_name = 'events/event_update_form.html'
    form_class = UpdateEventForm
    event = None

    def get(self, *args, **kwargs):
        event_id = self.kwargs['pk']
        self.event = get_events_from_db(event_id=event_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.event:
            kwargs['instance'] = self.event
        return kwargs


form_update_event = EventUpdateForm.as_view()


class EventsList(TemplateResponseMixin, ContextMixin, View):

    template_name = 'events/event_list.html'
    events_list = None
    organization_id = None

    def get(self, *args, **kwargs):
        self.events_list = self.get_events_from_services()
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.events_list:
            context['events'] = self.events_list
        if self.organization_id:
            context['organization_id'] = self.organization_id
        return context

    def get_events_from_services(self):
        self.organization_id = self.kwargs['pk']
        events = get_events_from_db(organization_id=self.organization_id)
        return events


events_list = EventsList.as_view()


class EventProfile(TemplateResponseMixin, FormMixin, View):

    template_name = 'events/event_profile.html'
    form_class = CreateRecordForm
    event = None
    records = None
    event_id = None

    def get(self, *args, **kwargs):
        self.event_id = self.kwargs['pk']
        self.event = get_event_profile_from_db(event_id=self.event_id)
        self.records = get_records_from_db(event_id=self.event_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.event:
            context['event'] = self.event
        if self.records:
            context['records'] = self.records
        if self.event_id:
            context['event_id'] = self.event_id
        return context

    def get_initial(self):
        initial = {
            'event_id': self.kwargs['pk']
        }
        return initial


event_profile = EventProfile.as_view()


class EventsUpdate(TemplateResponseMixin, FormMixin, View):

    template_name = 'events/event_update.html'
    form_class = UpdateEventForm
    event = None

    def get_event_from_services(self):
        event_id = self.kwargs['pk']
        event = get_events_from_db(event_id=event_id)
        return event

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.event:
            kwargs['instance'] = self.event
        return kwargs

    def post(self, *args, **kwargs):
        self.event = self.get_event_from_services()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        update_event_in_db(self.event, form)
        return redirect('event_profile', pk=self.event.pk)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)


events_update = EventsUpdate.as_view()


class EventsDelete(View):

    def post(self, *args, **kwargs):
        event_id = self.kwargs['pk']
        event = get_events_from_db(event_id=event_id)
        delete_event_from_db(event)
        return HttpResponse(status=200)


events_delete = EventsDelete.as_view()


# CRUD Record
class RecordCreate(TemplateResponseMixin, FormMixin, View):

    template_name = 'records/record_create.html'
    form_class = CreateRecordForm
    event = None
    record = None

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

    def post(self, *args, **kwargs):
        event_id = self.kwargs['pk']
        self.event = get_events_from_db(event_id=event_id)
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.record = create_record_in_db(self.event, form)
        context = self.get_context_data()
        return self.render_to_response(context=context)


record_create = RecordCreate.as_view()


class RecordCreateForm(TemplateResponseMixin, FormMixin, View):

    template_name = 'records/record_create_form.html'
    form_class = CreateRecordForm

    def get(self, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_initial(self):
        initial = {
            'event_id': self.kwargs['pk']
        }
        return initial


form_create_record = RecordCreateForm.as_view()


class RecordUpdateForm(TemplateResponseMixin, FormMixin, View):
    ...


form_update_record = RecordUpdateForm.as_view()


class RecordsList(TemplateResponseMixin, ContextMixin, View):

    template_name = 'records/record_list.html'
    records = None
    event_id = None

    def get(self, *args, **kwargs):
        self.event_id = self.kwargs['pk']
        self.records = get_records_from_db(event_id=self.event_id)
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.records:
            context['records'] = self.records
        if self.event_id:
            context['event_id'] = self.event_id
        return context


records_list = RecordsList.as_view()


class RecordUpdate(TemplateResponseMixin, FormMixin, View):
    ...


record_update = RecordUpdate.as_view()


class RecordDelete(TemplateResponseMixin, FormMixin, View):
    ...


record_delete = RecordDelete.as_view()

