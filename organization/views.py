from crispy_forms.utils import render_crispy_form
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context_processors import csrf
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.shortcuts import reverse

from organization.forms import CreateOrganizationForm, OrganizationUpdateForm, UpdateEventForm, CreateEventForm, \
    UpdateEmployeeForm, CreateEmployeeForm
from organization.models import Organizations, Events, Employees
from organization.services import db_function


class CreateOrganization(CreateView):

    template_name = 'organization_form.html'
    form_class = CreateOrganizationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'].update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        success_url = self.get_success_url()
        response = HttpResponse(status=302, headers={
            'Location': success_url,
        })
        return response

    def form_invalid(self, form):
        ctx = {}
        ctx.update(csrf(self.request))
        form_crispy = render_crispy_form(form, context=ctx)
        return HttpResponse(form_crispy)

    def get_success_url(self):
        return reverse('organization_profile')


organization_create = CreateOrganization.as_view()


class OrganizationProfile(DetailView):

    queryset = Organizations.objects.select_related('category')
    template_name = 'profile_organization.html'
    context_object_name = 'organization'

    def get_object(self, queryset=None):
        user = self.request.user.id
        if user is not None:
            queryset = self.queryset.filter(user_id=user)
        try:
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            pass
        else:
            return obj

    def get(self, request, *args, **kwargs):
        if not self.request.user.organization_created:
            return self.render_to_response(context=None)
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


organization_profile = OrganizationProfile.as_view()


class OrganizationUpdate(UpdateView):

    form_class = OrganizationUpdateForm
    queryset = Organizations.objects.select_related('category')
    template_name = 'organization_form.html'

    def form_invalid(self, form):
        ctx = {}
        ctx.update(csrf(self.request))
        form_crispy = render_crispy_form(form, context=ctx)
        return HttpResponse(form_crispy)

    def get_success_url(self):
        return reverse('organization_profile')


organization_update = OrganizationUpdate.as_view()


class OrganizationDelete(DeleteView):

    queryset = Organizations.objects.all()

    def get_success_url(self):
        return reverse('organization_profile')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        response = HttpResponse(status=302, headers={
            'Location': success_url,
        })
        return response


organization_delete = OrganizationDelete.as_view()


# CRUD Employee
class EmployeeCreate(CreateView):

    form_class = CreateEmployeeForm
    template_name = 'employee_form.html'

    def get(self, request, *args, **kwargs):
        self.object = None
        if self.request.user.organization_created:
            return super().get(request, *args, **kwargs)
        pass

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'].update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        ctx = {}
        ctx.update(csrf(self.request))
        form_crispy = render_crispy_form(form, context=ctx)
        return HttpResponse(form_crispy)

    def get_success_url(self):
        return reverse('employee_profile')


employee_create = EmployeeCreate.as_view()


class EmployeeProfile(ListView):

    template_name = 'employee_list.html'
    context_object_name = 'employees'

    def get_queryset(self):
        user = self.request.user
        if user is not None:
            queryset = user.employees
            return queryset.all()


employee_profile = EmployeeProfile.as_view()


class EmployeeUpdate(UpdateView):

    form_class = UpdateEmployeeForm
    template_name = 'employee_form.html'
    queryset = Employees.objects.all()

    def get_success_url(self):
        return reverse('employee_profile')


employee_update = EmployeeUpdate.as_view()


class EmployeeDelete(DeleteView):

    queryset = Employees.objects.all()

    def get_success_url(self):
        return reverse('employee_profile')


employee_delete = EmployeeDelete.as_view()


# CRUD Events
class EventsCreate(CreateView):

    template_name = 'events_form.html'
    form_class = CreateEventForm
    context_object_name = 'events'

    def get(self, request, *args, **kwargs):
        if self.request.user.organization_created:
            return super().get(request, *args, **kwargs)
        pass

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'].update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        ctx = {}
        ctx.update(csrf(self.request))
        form_crispy = render_crispy_form(form, context=ctx)
        return HttpResponse(form_crispy)

    def get_success_url(self):
        return reverse('event_profile')


events_create = EventsCreate.as_view()


class EventsProfile(ListView):

    template_name = 'events_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        user = self.request.user
        queryset = user.events.values('id', 'name', 'employees__name')
        obj = db_function(queryset)
        return obj


events_profile = EventsProfile.as_view()


class EventsUpdate(UpdateView):

    form_class = UpdateEventForm
    template_name = 'events_form.html'
    queryset = Events.objects.all()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'].update({
            'user': self.request.user
        })
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('event_profile')


events_update = EventsUpdate.as_view()


class EventsDelete(DeleteView):

    queryset = Events.objects.all()

    def get_success_url(self):
        return reverse('event_profile')


events_delete = EventsDelete.as_view()