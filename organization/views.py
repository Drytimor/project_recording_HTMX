from crispy_forms.utils import render_crispy_form
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import reverse, redirect
from django.template.context_processors import csrf
from django.views.generic import View
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.template.response import TemplateResponse
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.edit import FormMixin, BaseDeleteView

from organization.forms import CreateOrganizationForm, OrganizationUpdateForm, CreateEmployeeForm, UpdateEmployeeForm, \
    CreateEventForm, UpdateEventForm
from organization.models import Organizations, Employees, Events
from organization.services import create_organization_from_db, get_organization_from_db, delete_organization_from_db, \
    update_organization_in_db, get_employees_from_db, create_employee_in_db, update_employee_in_db, \
    delete_employee_from_db, create_event_in_db, update_event_in_db, get_events_from_db, delete_event_from_db


class CreateOrganization(TemplateResponseMixin, FormMixin, View):

    form_class = CreateOrganizationForm
    template_name = 'organization_form.html'
    user = None

    def get(self, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def post(self, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.user = self.request.user
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        create_organization_from_db(self.user, form)
        return redirect('organization_profile')

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)


organization_create = CreateOrganization.as_view()


class OrganizationProfile(TemplateResponseMixin, ContextMixin, View):

    organization = None
    template_name = 'profile_organization.html'

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

    template_name = 'organization_form.html'
    form_class = OrganizationUpdateForm
    organization = None

    def get(self, *args, **kwargs):
        self.organization = self.get_organization_from_services()
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.organization:
            kwargs.update({"instance": self.organization})
        return kwargs

    def get_organization_from_services(self):
        organization_id = self.kwargs['pk']
        organization = get_organization_from_db(organization_id=organization_id)
        return organization

    def post(self, *args, **kwargs):
        self.organization = self.get_organization_from_services()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        update_organization_in_db(self.organization, form)
        return redirect('organization_profile')

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)


organization_update = OrganizationUpdate.as_view()


class OrganizationDelete(View):

    def post(self, *args, **kwargs):
        user = self.request.user
        delete_organization_from_db(user)
        return redirect('organization_profile')


organization_delete = OrganizationDelete.as_view()


class EmployeeCreate(TemplateResponseMixin, FormMixin, View):

    template_name = 'employee_form.html'
    form_class = CreateEmployeeForm
    organization_id = None

    def get(self, *args, **kwargs):
        self.organization_id = self.get_organization_id_from_request()
        context = self.get_context_data()
        return self.render_to_response(context=context)

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
        create_employee_in_db(self.organization_id, form)
        return redirect('employees_list', pk=self.organization_id)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)


employee_create = EmployeeCreate.as_view()


class EmployeesList(TemplateResponseMixin, ContextMixin, View):

    template_name = 'employee_list.html'
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


class EmployeeUpdate(TemplateResponseMixin, FormMixin, View):

    template_name = 'employee_form.html'
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

    def post(self, *args, **kwargs):
        self.employee = self.get_employee_from_services()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        update_employee_in_db(self.employee, form)
        return redirect('employees_list', pk=self.employee.organization_id)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)


employee_update = EmployeeUpdate.as_view()


class EmployeeDelete(View):

    employee = None

    def post(self, request, *args, **kwargs):
        employee_id = self.kwargs['pk']
        self.employee = get_employees_from_db(employee_id=employee_id)
        delete_employee_from_db(self.employee)
        return redirect('employees_list', pk=self.employee.organization_id)


employee_delete = EmployeeDelete.as_view()


class EventsCreate(TemplateResponseMixin, FormMixin, View):

    template_name = 'event_form.html'
    form_class = CreateEventForm
    organization_id = None

    def get(self, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_initial(self):
        initial = {
            'organization_id': self.get_organization_id_from_request()
        }
        return initial

    def get_organization_id_from_request(self):
        return self.kwargs['pk']

    def post(self, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.organization_id = self.get_organization_id_from_request()
        create_event_in_db(self.organization_id, form)
        return redirect('events_list', pk=self.organization_id)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)


events_create = EventsCreate.as_view()


class EventsList(TemplateResponseMixin, ContextMixin, View):

    template_name = 'event_list.html'
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


class EventsUpdate(TemplateResponseMixin, FormMixin, View):

    template_name = 'event_form.html'
    form_class = UpdateEventForm
    event = None

    def get(self, *args, **kwargs):
        self.event = self.get_event_from_services()
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.event:
            kwargs['instance'] = self.event
        return kwargs

    def get_event_from_services(self):
        event_id = self.kwargs['pk']
        event = get_events_from_db(event_id=event_id)
        return event

    def post(self, *args, **kwargs):
        self.event = self.get_event_from_services()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        update_event_in_db(self.event, form)
        return redirect('events_list', pk=self.event.organization_id)

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)


events_update = EventsUpdate.as_view()


class EventsDelete(View):

    event = None

    def post(self, *args, **kwargs):
        event_id = self.kwargs['pk']
        self.event = get_events_from_db(event_id=event_id)
        delete_event_from_db(self.event)
        return redirect('events_list', pk=self.event.organization_id)


events_delete = EventsDelete.as_view()

