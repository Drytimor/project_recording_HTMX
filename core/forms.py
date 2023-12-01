from allauth.account.forms import (SignupForm, LoginForm, ResetPasswordForm, ChangePasswordForm, AddEmailForm,
                                   ResetPasswordKeyForm)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button, ButtonHolder, HTML, Layout, Field, Fieldset
from django.urls import reverse_lazy, NoReverseMatch
from django.utils.safestring import mark_safe
from django.forms import forms, EmailField, CharField
from crispy_forms_foundation.layout.buttons import ButtonElement


class MyCustomSignupForm(SignupForm):

    def __init__(self, *args, **kwargs):
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
            'hx-target': '#create-user-form',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit('submit', 'Зарегистрироваться'))


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
            'hx-target': '#auth-user-form',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit('submit', 'Войти'))


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
            'hx-target': '#reset-password-user-form',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit('submit', 'Отправить'))


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
        self.helper.add_input(Submit('submit', 'Отправить'))


class MyCustomResetPasswordKeyForm(ResetPasswordKeyForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'reset-password-key-user-form'
        self.helper.attrs = {
            'hx-post': '',
            'hx-target': '#reset-password-key-user-form',
            'hx-swap': 'outerHTML',
            'hx-select': '#reset-password-key-user-form',
        }
        self.helper.add_input(Submit('action', 'Отправить'))


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
        self.helper.add_input(Submit('action_add', 'Отправить'))


class MyCrispyForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset('', 'email', 'name'),
            Button('Save', 'save', css_class=' btn-secondary'),
            ButtonElement('google', 'google',
                          css_class='btn btn-outline-info',
                          content="<a href='/accounts/google/login/?next=/' > Google </a>")
        )

    email = EmailField()
    name = CharField(required=False)

