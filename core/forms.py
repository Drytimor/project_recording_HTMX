from allauth.account.forms import (SignupForm, LoginForm, ResetPasswordForm, ChangePasswordForm, AddEmailForm,
                                   ResetPasswordKeyForm, SetPasswordForm)
from allauth.socialaccount.templatetags.socialaccount import provider_login_url
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy, NoReverseMatch
from django.utils.safestring import mark_safe
from django import forms
from .models import Organizations, Categories, Events, Employees


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
            'hx-post': reverse_lazy('profile_update'),
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


class CreateOrganizationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'central-col'
        self.helper.attrs = {
            'hx-post': reverse_lazy('organization_create'),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Создать'))

        self.helper.add_input(Button(name='button',
                                     value='Отмена',
                                     css_class='btn',
                                     hx_get=reverse_lazy('organization_profile'),
                                     hx_target='#central-col',
                                     hx_swap="innerHTML"))

    category = forms.ModelChoiceField(label='Категория',
                                      queryset=Categories.objects.all(),
                                      widget=forms.RadioSelect)

    def save(self, commit=True):
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate."
                % (
                    self.instance._meta.object_name,
                    "created" if self.instance._state.adding else "changed",
                )
            )
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save(user=self.initial['user'])

    class Meta:
        model = Organizations
        fields = ('name', 'category')


class OrganizationUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'central-col'
        self.helper.attrs = {
            'hx-post': reverse_lazy('organization_update'),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Изменить'))

        self.helper.add_input(Button(name='button',
                                     value='Отмена',
                                     css_class='btn',
                                     hx_get=reverse_lazy('organization_profile'),
                                     hx_target="#central-col",
                                     hx_swap="innerHTML"))

    def save(self, commit=True):
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate."
                % (
                    self.instance._meta.object_name,
                    "created" if self.instance._state.adding else "changed",
                )
            )
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save(user=self.initial['user'])

    class Meta:
        model = Organizations
        fields = ('name', 'category')
        widgets = {
            'category': forms.RadioSelect
        }


class CreateEventForm(forms.ModelForm):

    employees = forms.ModelMultipleChoiceField(queryset=Employees.objects.none(),
                                               widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._organization = self.initial['organization']
        self.fields['employees'].queryset = Employees.objects.get_employees_org(self.organization.pk)
        self.helper = FormHelper(self)
        self.helper.form_id = 'central-col'
        self.helper.attrs = {
            'hx-post': reverse_lazy('event_create'),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Создать'))

        self.helper.add_input(Button(name='button',
                                     value='Отмена',
                                     css_class='btn',
                                     hx_get=reverse_lazy('event_profile'),
                                     hx_target='#central-col',
                                     hx_swap="innerHTML"))

    @property
    def organization(self):
        return self._organization

    def save(self, commit=True):
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate."
                % (
                    self.instance._meta.object_name,
                    "created" if self.instance._state.adding else "changed",
                )
            )
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save(organization=self.organization)

    class Meta:
        model = Events
        fields = ('name', 'employees')


class UpdateEventForm(forms.ModelForm):

    employees = forms.ModelMultipleChoiceField(queryset=Employees.objects.none(),
                                               widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._organization_id = self.initial['organization_id']
        self.fields['employees'].queryset = Employees.objects.get_employees_org(self.organization_id)
        self.helper = FormHelper(self)
        self.helper.form_id = 'central-col'
        self.helper.attrs = {
            'hx-post': reverse_lazy('event_update', kwargs={
                'pk': self.instance.pk
            }),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Изменить'))

        self.helper.add_input(Button(name='button',
                                     value='Отмена',
                                     css_class='btn',
                                     hx_get=reverse_lazy('event_profile'),
                                     hx_target='#central-col',
                                     hx_swap="innerHTML"))

    @property
    def organization_id(self):
        return self._organization_id

    class Meta:
        model = Events
        fields = ('name', 'employees')


class CreateEmployeeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'central-col'
        self.helper.attrs = {
            'hx-post': reverse_lazy('employee_create'),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Создать'))

        self.helper.add_input(Button(name='button',
                                     value='Отмена',
                                     css_class='btn',
                                     hx_get=reverse_lazy('employee_profile'),
                                     hx_target='#central-col',
                                     hx_swap="innerHTML"))

    def save(self, commit=True):
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate."
                % (
                    self.instance._meta.object_name,
                    "created" if self.instance._state.adding else "changed",
                )
            )
        if commit:
            # If committing, save the instance and the m2m data immediately.
            self.instance.save(organization=self.initial['organization'])

    class Meta:
        model = Employees
        fields = ('name',)


class UpdateEmployeeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'central-col'
        self.helper.attrs = {
            'hx-post': reverse_lazy('employee_update', kwargs={
                'pk': self.instance.pk
            }),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Изменить'))

        self.helper.add_input(Button(name='button',
                                     value='Отмена',
                                     css_class='btn',
                                     hx_get=reverse_lazy('employee_profile'),
                                     hx_target='#central-col',
                                     hx_swap="innerHTML"))

    class Meta:
        model = Employees
        fields = ('name',)
