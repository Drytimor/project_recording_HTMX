from crispy_forms.utils import render_crispy_form
from django.shortcuts import render, reverse, redirect
from django.views.generic import TemplateView, View, UpdateView, CreateView, DetailView, DeleteView, ListView
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import ContextMixin
from .forms import UserUpdateForm, CreateEmployeeForm, \
    UpdateEmployeeForm, CreateEventForm, UpdateEventForm
from .models import User, Organizations, Employees, Events
from django.template import loader
from django.template.context_processors import csrf
from allauth.account.views import SignupView


class Home(TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


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
                            headers={'HX-Trigger': 'updateNav'})


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

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

    def get_object(self, queryset=None):
        pk = self.request.user.id
        queryset = self.queryset.filter(pk=pk)
        obj = queryset.get()
        return obj

    def get_success_url(self):
        return reverse('profile_htmx')





# CRUD Employee
class EmployeeCreate(CreateView):

    form_class = CreateEmployeeForm
    template_name = 'employee_form.html'

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
        user = self.request.user.pk
        queryset = Employees.objects.filter(user_id=user)
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'].update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

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
        user = self.request.user.pk
        queryset = Events.objects.filter(user_id=user)
        return queryset.all()


events_profile = EventsProfile.as_view()


class EventsUpdate(UpdateView):

    form_class = UpdateEventForm
    template_name = 'events_form.html'
    queryset = Events.objects.all()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'].update({
            'user_id': self.request.user.pk
        })
        return kwargs

    def get_success_url(self):
        return reverse('event_profile')


events_update = EventsUpdate.as_view()


class EventsDelete(DeleteView):

    queryset = Events.objects.all()

    def get_success_url(self):
        return reverse('event_profile')


events_delete = EventsDelete.as_view()

