from crispy_forms.utils import render_crispy_form
from django.shortcuts import render, reverse, redirect
from django.views.generic import TemplateView, View, UpdateView, DeleteView, ListView, CreateView, DetailView
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateResponseMixin, ContextMixin
from django.views.generic.edit import FormMixin
from .forms import UserUpdateForm
from django.template import loader
from django.template.context_processors import csrf
from allauth.account.views import SignupView
from .services import update_user_from_db, delete_user_from_db


class Home(TemplateResponseMixin, ContextMixin, View):
    template_name = 'base.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context=context,
                                       headers={'HX-Trigger-After-Swap': 'AnonymUser'})


home = Home.as_view()


class AuthRedirect(View):

    def get(self, *args, **kwargs):
        return HttpResponse(content='OK',
                            headers={'HX-Trigger-After-Swap': 'AuthUser'}
                            )


auth_redirect = AuthRedirect.as_view()


class Logout(View):

    def get(self, *args, **kwargs):
        return redirect('home')


logout_redirect = Logout.as_view()


class PasswordResetFromKeyDoneView(View):

    def get(self, *args, **kwargs):
        template = loader.get_template('account/password_reset_from_key_done.html')
        return HttpResponse(template.render(request=self.request),
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

    def get(self, *args, **kwargs):
        return render(self.request, 'profile.html')


profile = Profile.as_view()


class ProfileHTMX(View):

    def get(self, *args, **kwargs):
        return render(self.request, 'profile_htmx.html')


profile_htmx = ProfileHTMX.as_view()


class ProfileUpdate(TemplateResponseMixin, FormMixin, View):

    template_name = 'profile_update_form.html'
    form_class = UserUpdateForm
    user = None

    def get(self, request, *args, **kwargs):
        self.user = request.user
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.user:
            kwargs['instance'] = self.user
        return kwargs

    def post(self, request, *args, **kwargs):
        self.user = request.user
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        update_user_from_db(self.user, form)
        return redirect('profile_htmx')

    def form_invalid(self, form):
        form_crispy = render_crispy_form(form, context=csrf(self.request))
        return HttpResponse(form_crispy)


profile_update = ProfileUpdate.as_view()


class ProfileDelete(View):

    def post(self, request, *args, **kwargs):
        delete_user_from_db(request.user)
        return HttpResponseRedirect(reverse('home'),
                                    headers={
                                        'HX-Replace-Url': 'http://127.0.0.1:8000/'
                                    })


profile_delete = ProfileDelete.as_view()


