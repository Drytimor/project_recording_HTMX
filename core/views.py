from crispy_forms.utils import render_crispy_form
from django.shortcuts import render, reverse
from django.views.generic import TemplateView, View, UpdateView,  DeleteView
from django.http import HttpResponse
from django.views.generic.base import ContextMixin
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

