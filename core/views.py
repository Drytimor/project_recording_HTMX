from django.shortcuts import render
from django.views.generic import TemplateView, View, DetailView
from django.http import HttpResponse

from .forms import MyCrispyForm
from .models import User
from django.template import loader


class Home(TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.__setitem__('form', MyCrispyForm)
        return context


class UpdateNav(View):

    def get(self, request, *args, **kwargs):
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
        return HttpResponse('OK', headers={'HX-Trigger': 'updateNav'})


class Logout(View):

    def get(self, request):
        return HttpResponse(headers={'HX-Trigger': 'CleanProfile, updateNav'})


class Profile(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'profile.html')


class ProfileHTMX(DetailView):

    template_name = 'profile_htmx.html'
    queryset = User.objects.all()


class PasswordResetFromKeyDoneView(View):

    def get(self,request,  *args, **kwargs):
        template = loader.get_template('account/password_reset_from_key_done.html')
        return HttpResponse(template.render(request=request),
                            headers={'HX-Trigger': 'updateNav',
                                     'HX-Replace-Url': '/'})



password_reset_from_key_done = PasswordResetFromKeyDoneView.as_view()


