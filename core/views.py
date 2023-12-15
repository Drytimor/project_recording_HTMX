from crispy_forms.utils import render_crispy_form
from django.shortcuts import render, reverse
from django.views.generic import TemplateView, View, UpdateView, DeleteView, ListView, CreateView, DetailView
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic.base import ContextMixin

from organization.forms import UpdateEventForm, CreateEventForm, UpdateEmployeeForm, CreateEmployeeForm, \
    OrganizationUpdateForm, CreateOrganizationForm
from organization.models import Events, Employees, Organizations
from .forms import UserUpdateForm
from .models import User
from django.template import loader
from django.template.context_processors import csrf
from allauth.account.views import SignupView


class Home(TemplateView):
    template_name = 'base.html'


class UpdateNav(View):

    def get(self, request, *args, **kwargs):
        if self.request.headers['Trigger'] == 'updateNav':
            if request.user.is_anonymous:
                return render(request, 'anonym_user_nav_bar.html')
            return render(request, 'auth_user_nav_bar.html')


class CleanProfile(View):

    def get(self, request):
        return render(request, 'home.html')


class AuthRedirect(View):

    def get(self, request):
        if request.user.is_anonymous:
            return HttpResponse(headers={'HX-Trigger': 'updateNav'})
        return HttpResponse(content='OK',
                            headers={'HX-Trigger': 'updateNav'}
                            )


class Logout(View):

    def get(self, request):
        return HttpResponse(headers={'HX-Trigger': 'CleanProfile, updateNav'})


class PasswordResetFromKeyDoneView(View):

    def get(self, request,  *args, **kwargs):
        template = loader.get_template('account/password_reset_from_key_done.html')
        return HttpResponse(template.render(request=request),
                            headers={'HX-Trigger': 'updateNav',
                                     'HX-Replace-Url': '/'})


password_reset_from_key_done = PasswordResetFromKeyDoneView.as_view()


class CustomSignupView(SignupView):

    def get_form_kwargs(self):
        kwargs = super(CustomSignupView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


signup = CustomSignupView.as_view()


class Profile(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'profile.html')


class ProfileHTMX(View, ContextMixin):

    def get(self, request, *args, **kwargs):
        return render(request, 'profile_htmx.html')


class ProfileUpdate(UpdateView):

    template_name = 'profile_update_form.html'
    form_class = UserUpdateForm
    queryset = User.objects.only('username', 'first_name', 'last_name')

    def form_invalid(self, form):
        ctx = {}
        ctx.update(csrf(self.request))
        form_crispy = render_crispy_form(form, context=ctx)
        return HttpResponse(form_crispy)

    def get_success_url(self):
        return reverse('profile_htmx')


class ProfileDelete(DeleteView):

    queryset = User.objects.all()

    def form_valid(self, form):
        self.object.delete()
        return HttpResponse(headers={'HX-Trigger': 'CleanProfile, updateNav'})


profile_delete = ProfileDelete.as_view()

# # CRUD organization
# class CreateOrganization(CreateView):
#
#     template_name = 'organization_form.html'
#     form_class = CreateOrganizationForm
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['initial'].update({'user': self.request.user})
#         return kwargs
#
#     def form_valid(self, form):
#         self.object = form.save()
#         success_url = self.get_success_url()
#         response = HttpResponse(status=302, headers={
#             'Location': success_url,
#         })
#         return response
#
#     def form_invalid(self, form):
#         ctx = {}
#         ctx.update(csrf(self.request))
#         form_crispy = render_crispy_form(form, context=ctx)
#         return HttpResponse(form_crispy)
#
#     def get_success_url(self):
#         return reverse('organization_profile')
#
#
# organization_create = CreateOrganization.as_view()
#
#
# class OrganizationProfile(DetailView):
#
#     queryset = Organizations.objects.select_related('category')
#     template_name = 'profile_organization.html'
#     context_object_name = 'organization'
#
#     def get_object(self, queryset=None):
#         user = self.request.user.id
#         if user is not None:
#             queryset = self.queryset.filter(user_id=user)
#         try:
#             obj = queryset.get()
#         except queryset.model.DoesNotExist:
#             pass
#         else:
#             return obj
#
#     def get(self, request, *args, **kwargs):
#         if not self.request.user.organization_created:
#             return self.render_to_response(context=None)
#         self.object = self.get_object()
#         context = self.get_context_data(object=self.object)
#         return self.render_to_response(context)
#
#
# organization_profile = OrganizationProfile.as_view()
#
#
# class OrganizationUpdate(UpdateView):
#
#     form_class = OrganizationUpdateForm
#     queryset = Organizations.objects.select_related('category')
#     template_name = 'organization_form.html'
#
#     def form_invalid(self, form):
#         ctx = {}
#         ctx.update(csrf(self.request))
#         form_crispy = render_crispy_form(form, context=ctx)
#         return HttpResponse(form_crispy)
#
#     def get_success_url(self):
#         return reverse('organization_profile')
#
#
# organization_update = OrganizationUpdate.as_view()
#
#
# class OrganizationDelete(DeleteView):
#
#     queryset = Organizations.objects.all()
#
#     def get_success_url(self):
#         return reverse('organization_profile')
#
#     def form_valid(self, form):
#         success_url = self.get_success_url()
#         self.object.delete()
#         response = HttpResponse(status=302, headers={
#             'Location': success_url,
#         })
#         return response
#
#
# organization_delete = OrganizationDelete.as_view()
#
#
# # CRUD Employee
# class EmployeeCreate(CreateView):
#
#     form_class = CreateEmployeeForm
#     template_name = 'employee_form.html'
#
#     def get(self, request, *args, **kwargs):
#         self.object = None
#         if self.request.user.organization_created:
#             return super().get(request, *args, **kwargs)
#         pass
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['initial'].update({'user': self.request.user})
#         return kwargs
#
#     def form_valid(self, form):
#         self.object = form.save()
#         return HttpResponseRedirect(self.get_success_url())
#
#     def form_invalid(self, form):
#         ctx = {}
#         ctx.update(csrf(self.request))
#         form_crispy = render_crispy_form(form, context=ctx)
#         return HttpResponse(form_crispy)
#
#     def get_success_url(self):
#         return reverse('employee_profile')
#
#
# employee_create = EmployeeCreate.as_view()
#
#
# class EmployeeProfile(ListView):
#
#     template_name = 'employee_list.html'
#     context_object_name = 'employees'
#
#     def get_queryset(self, organization_id):
#         queryset = Employees.objects.filter(organization_id=organization_id)
#         return queryset.all()
#
#     def get(self, request, *args, **kwargs):
#         self.organization_id = self.kwargs['pk']
#         self.object_list = self.get_queryset(self.organization_id)
#         allow_empty = self.get_allow_empty()
#
#         if not allow_empty:
#             # When pagination is enabled and object_list is a queryset,
#             # it's better to do a cheap query than to load the unpaginated
#             # queryset in memory.
#             if self.get_paginate_by(self.object_list) is not None and hasattr(
#                 self.object_list, "exists"
#             ):
#                 is_empty = not self.object_list.exists()
#             else:
#                 is_empty = not self.object_list
#             if is_empty:
#                 from wheel.metadata import _
#                 raise Http404(
#                     _("Empty list and “%(class_name)s.allow_empty” is False.")
#                     % {
#                         "class_name": self.__class__.__name__,
#                     }
#                 )
#         context = self.get_context_data()
#         return self.render_to_response(context)
#
#     def get_context_data(self,*args, **kwargs):
#         context = super().get_context_data(*args, **kwargs)
#         context['organization'] = self.organization_id
#
#
# employee_profile = EmployeeProfile.as_view()
#
#
# class EmployeeUpdate(UpdateView):
#
#     form_class = UpdateEmployeeForm
#     template_name = 'employee_form.html'
#     queryset = Employees.objects.all()
#
#     def get_success_url(self):
#         return reverse('employee_profile')
#
#
# employee_update = EmployeeUpdate.as_view()
#
#
# class EmployeeDelete(DeleteView):
#
#     queryset = Employees.objects.all()
#
#     def get_success_url(self):
#         return reverse('employee_profile')
#
#
# employee_delete = EmployeeDelete.as_view()
#
#
# # CRUD Events
# class EventsCreate(CreateView):
#
#     template_name = 'event_form.html'
#     form_class = CreateEventForm
#     context_object_name = 'events'
#
#     def get(self, request, *args, **kwargs):
#         if self.request.user.organization_created:
#             return super().get(request, *args, **kwargs)
#         pass
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['initial'].update({'user': self.request.user})
#         return kwargs
#
#     def form_valid(self, form):
#         self.object = form.save()
#         return HttpResponseRedirect(self.get_success_url())
#
#     def form_invalid(self, form):
#         ctx = {}
#         ctx.update(csrf(self.request))
#         form_crispy = render_crispy_form(form, context=ctx)
#         return HttpResponse(form_crispy)
#
#     def get_success_url(self):
#         return reverse('event_profile')
#
#
# events_create = EventsCreate.as_view()
#
#
# class EventsProfile(ListView):
#
#     template_name = 'events_list.html'
#     context_object_name = 'events'
#
#     def get_queryset(self):
#         user = self.request.user
#         queryset = user.events.values('id', 'name', 'employees__name')
#         obj = db_function(queryset)
#         return obj
#
#
# events_profile = EventsProfile.as_view()
#
#
# class EventsUpdate(UpdateView):
#
#     form_class = UpdateEventForm
#     template_name = 'event_form.html'
#     queryset = Events.objects.all()
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['initial'].update({
#             'user': self.request.user
#         })
#         return kwargs
#
#     def form_valid(self, form):
#         self.object = form.save()
#         return HttpResponseRedirect(self.get_success_url())
#
#     def get_success_url(self):
#         return reverse('event_profile')
#
#
# events_update = EventsUpdate.as_view()
#
#
# class EventsDelete(DeleteView):
#
#     queryset = Events.objects.all()
#
#     def get_success_url(self):
#         return reverse('event_profile')
#
#
# events_delete = EventsDelete.as_view()


