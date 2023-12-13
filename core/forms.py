from allauth.account.adapter import get_adapter
from allauth.account.forms import (SignupForm, LoginForm, ResetPasswordForm, ChangePasswordForm, AddEmailForm,
                                   ResetPasswordKeyForm, SetPasswordForm)
from allauth.account.models import EmailAddress
from allauth.account.utils import setup_user_email
from allauth.socialaccount.templatetags.socialaccount import provider_login_url
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy, NoReverseMatch
from django.utils.safestring import mark_safe
from django import forms


class MyCustomSignupForm(SignupForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        try:
            login_url = reverse_lazy('account_login')
        except NoReverseMatch:
            pass
        else:
            self.fields['password2'].help_text = mark_safe(
                f"<a hx-get='{login_url}' role='button'>Уже зарегистрированы? Войдите</a>"
            )
        self.helper = FormHelper(self)
        self.helper.form_id = 'create-user-form'
        self.helper.attrs = {
            'hx-post': reverse_lazy('account_signup'),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Зарегистрироваться'))

        self.helper.add_input(Button(name='button',
                                     value='Google',
                                     css_class='btn-outline-info',
                                     hx_get=provider_login_url(context={'request':
                                                                        self.request},
                                                               provider='google',
                                                               next='/')))
    is_organization = forms.BooleanField(label='Организация',
                                         required=False)

    def save(self, request):
        email = self.cleaned_data.get("email")
        if self.account_already_exists:
            raise ValueError(email)
        adapter = get_adapter()
        user = adapter.new_user(request)
        user.is_organization = self.cleaned_data['is_organization']  # присоединение роли
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [EmailAddress(email=email)] if email else [])
        return user


class MyCustomLoginFrom(LoginForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            reset_url = reverse_lazy('account_signup')
        except NoReverseMatch:
            pass
        else:
            self.fields['login'].help_text = mark_safe(
                f"<a hx-get='{reset_url}' role='button'>Не зарегистрированы?</a>"
            )
        try:
            reset_password_url = reverse_lazy('account_reset_password')
        except NoReverseMatch:
            pass
        else:
            self.fields['password'].help_text = mark_safe(
                f"<a hx-get='{reset_password_url}' role='button'>Забыли пароль?</a>"
            )
        self.fields['login'].label = 'Логин'
        self.helper = FormHelper(self)
        self.helper.form_id = 'auth-user-form'
        self.helper.attrs = {
            'hx-post': reverse_lazy('account_login'),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Войти',
                                     css_class='btn btn-primary'))

        self.helper.add_input(Button(name='button',
                                     value='Google',
                                     css_class='btn-outline-info',
                                     hx_get=provider_login_url(context={'request':
                                                                        self.request},
                                                               provider='google',
                                                               next='/')))


class MyCustomResetPasswordForm(ResetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields['email'].help_text = mark_safe(
            '<p>Введите свой адрес электронной почты, '
            'и мы вышлем вам электронное письмо, позволяющее сбросить ваш пароль.</p>'
        )
        self.helper.form_id = 'reset-password-user-form'
        self.helper.attrs = {
            'hx-post': reverse_lazy('account_reset_password'),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Отправить письмо'))


class MyCustomChangePasswordForm(ChangePasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            reset_password_url = reverse_lazy('account_reset_password')
        except NoReverseMatch:
            pass
        else:
            self.fields['oldpassword'].help_text = mark_safe(
                f"<a hx-get='{reset_password_url}' role='button'>Забыли пароль?</a>"
            )
        self.helper = FormHelper(self)

        self.helper.form_id = 'change-password-user-form'
        self.helper.attrs = {
            'hx-post': reverse_lazy('account_change_password'),
            'hx-target': '#modal-form',
            'hx-swap': 'innerHTML',
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Изменить пароль'))


class MyCustomResetPasswordKeyForm(ResetPasswordKeyForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'reset-password-key-user-form'
        self.helper.attrs = {
            'hx-post': '',
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
            'hx-select': '#reset-password-key-user-form',
        }
        self.helper.add_input(Submit(name='action',
                                     value='Сбросить пароль'))


class MyCustomSetPasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'set-password-user-form'
        self.helper.attrs = {
            'hx-post': reverse_lazy('account_set_password'),
            'hx-target': '#modal-form',
            'hx-swap': 'innerHTML',
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Установить пароль'))


class MyCustomAddEmailForm(AddEmailForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'email-account-user-form'
        self.helper.attrs = {
            'hx-post': reverse_lazy('account_email'),
            'hx-target': '#modal-form',
            'hx-swap': 'innerHTML',
        }
        self.helper.add_input(Submit(name='action_add',
                                     value='Изменить Email'))


class UserUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'central-col'
        self.helper.attrs = {
            'hx-post': reverse_lazy('profile_update', kwargs={
                'pk': self.instance.pk
            }),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
            'hx-select': '#central-col'
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Изменить'))

        self.helper.add_input(Button(name='button',
                                     value='Отмена',
                                     css_class='btn',
                                     hx_get=reverse_lazy('profile_htmx'),
                                     hx_target="#central-col",
                                     hx_select="#central-col",
                                     hx_swap="outerHTML"))

    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name')

