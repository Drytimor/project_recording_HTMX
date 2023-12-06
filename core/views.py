from crispy_forms.utils import render_crispy_form
from django.shortcuts import render, reverse, redirect
from django.views.generic import TemplateView, View, UpdateView, CreateView, DetailView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import ContextMixin
from .forms import UserUpdateForm, CreateOrganizationForm, OrganizationUpdateForm
from .models import User, Organizations
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


class CreateOrganization(CreateView):

    model = Organizations
    template_name = 'organization_create.html'
    form_class = CreateOrganizationForm

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
        return reverse('organization_profile')


organization_create = CreateOrganization.as_view()


class OrganizationProfile(DetailView):

    model = Organizations
    queryset = Organizations.objects.select_related('category')
    template_name = 'profile_organization.html'

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


organization_profile = OrganizationProfile.as_view()


class OrganizationUpdate(UpdateView):

    form_class = OrganizationUpdateForm
    queryset = Organizations.objects.select_related('category')
    template_name = 'organization_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'].update({'user': self.request.user})
        return kwargs

    def form_invalid(self, form):
        ctx = {}
        ctx.update(csrf(self.request))
        form_crispy = render_crispy_form(form, context=ctx)
        return HttpResponse(form_crispy)

    def get_object(self, queryset=None):
        user = self.request.user.id
        queryset = self.queryset.filter(user_id=user)
        obj = queryset.get()
        return obj

    def get_success_url(self):
        return reverse('organization_profile')


organization_update = OrganizationUpdate.as_view()


class OrganizationDelete(DeleteView):

    queryset = Organizations.objects.all()

    def get_object(self, queryset=None):
        user = self.request.user.id
        queryset = self.queryset.filter(user_id=user)
        obj = queryset.get()
        return obj

    def get_success_url(self):
        return reverse('organization_profile')


organization_delete = OrganizationDelete.as_view()


