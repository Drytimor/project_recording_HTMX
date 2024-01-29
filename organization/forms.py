from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button, Hidden
from django import forms
from django.urls import reverse_lazy
from organization.models import Categories, Organizations, Employees, Events, Records
import datetime


class CreateOrganizationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'org-create-form'
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
                                     css_id='',
                                     hx_get=reverse_lazy('organization_profile'),
                                     hx_target='#central-col',
                                     hx_select='#central-col',
                                     hx_swap="outerHTML"))

    category = forms.ModelChoiceField(label='Категория',
                                      queryset=Categories.objects.all(),
                                      widget=forms.RadioSelect)

    class Meta:
        model = Organizations
        fields = ('name', 'category')


class UpdateOrganizationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'org-update-form'
        self.helper.attrs = {
            'hx-post': reverse_lazy('organization_update', kwargs={
                'org_pk': self.instance.pk
            }),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',

        }
        self.helper.add_input(Submit(name='submit',
                                     value='Изменить'))

        self.helper.add_input(Button(name='button',
                                     value='Отмена',
                                     css_class='btn',
                                     hx_get=reverse_lazy('organization_profile'),
                                     hx_select='#central-col',
                                     hx_target="#org-update-form",
                                     hx_swap="outerHTML"))

    class Meta:
        model = Organizations
        fields = ('name', 'category')
        widgets = {
            'category': forms.RadioSelect
        }


class CreateEventForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._organization = self.initial['organization_id']
        self.fields['employees'].queryset = Employees.objects.filter(organization_id=self.organization)
        self.helper = FormHelper(self)
        self.helper.form_id = 'event-create-form'
        self.helper.attrs = {
            'hx-post': reverse_lazy('event_create',
                                    kwargs={
                                        'org_pk': self.organization
                                    }),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',

        }
        self.helper.add_input(Submit(name='submit',
                                     value='Создать'))

        self.helper.add_input(Button(name='button',
                                     value='Закрыть',
                                     css_class='btn',
                                     hx_get=reverse_lazy('event_profile'),
                                     hx_target='#event-create-form',
                                     hx_select='#event-profile',
                                     hx_swap="outerHTML"))

    employees = forms.ModelMultipleChoiceField(queryset=Employees.objects.none(),
                                               widget=forms.CheckboxSelectMultiple)

    @property
    def organization(self):
        return self._organization

    class Meta:
        model = Events
        fields = ('name', 'employees', 'status_tariff')


class UpdateEventForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employees'].queryset = Employees.objects.filter(organization_id=self.instance.organization_id)
        self.helper = FormHelper(self)
        self._organization = self.initial['organization_id']
        self.helper.form_id = 'event-update-form'
        self.helper.attrs = {
            'hx-post': reverse_lazy('event_update', kwargs={
                'event_pk': self.instance.pk,
                'org_pk': self.organization
            }),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
            'hx-select': '#event-profile'
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Изменить'))

        self.helper.add_input(Button(name='button',
                                     value='Отмена',
                                     css_class='btn',
                                     hx_get=reverse_lazy('event_profile',
                                                         kwargs={
                                                             'event_pk': self.instance.pk,
                                                             'org_pk': self.organization
                                                         }),
                                     hx_target='#event-update-form',
                                     hx_select='#event-profile',
                                     hx_swap="outerHTML"))

    employees = forms.ModelMultipleChoiceField(queryset=Employees.objects.none(),
                                               widget=forms.CheckboxSelectMultiple)

    @property
    def organization(self):
        return self._organization

    class Meta:
        model = Events
        fields = ('name', 'employees', 'status_tariff')


class CreateEmployeeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self._organization = self.initial['organization_id']
        self.helper.form_id = 'employee-create-form'
        self.helper.attrs = {
            'hx-post': reverse_lazy('employee_create',
                                    kwargs={
                                        'org_pk': self.organization
                                    }),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Создать'))

        self.helper.add_input(Button(name='button',
                                     value='Закрыть',
                                     css_class='btn',
                                     hx_get=reverse_lazy('employee_profile'),
                                     hx_target='#employee-create-form',
                                     hx_swap="outerHTML"))

    @property
    def organization(self):
        return self._organization

    class Meta:
        model = Employees
        fields = ('name',)


class UpdateEmployeeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self._organization = self.initial['organization_id']
        self.helper.form_id = 'employee-update-form'
        self.helper.attrs = {
            'hx-post': reverse_lazy('employee_update', kwargs={
                'emp_pk': self.instance.pk,
                'org_pk': self.organization
            }),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Изменить'))

        self.helper.add_input(Button(name='button',
                                     value='Отмена',
                                     css_class='btn',
                                     hx_get=reverse_lazy('employee_profile',
                                                         kwargs={
                                                             'emp_pk': self.instance.pk,
                                                             'org_pk': self.organization
                                                         }),
                                     hx_target='#employee-update-form',
                                     hx_swap="outerHTML"))

    @property
    def organization(self):
        return self._organization

    class Meta:
        model = Employees
        fields = ('name',)


class CreateRecordForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._event = self.initial['event_id']
        self.helper = FormHelper(self)
        self.helper.form_id = 'record-create-form'
        self.helper.attrs = {
            'hx-post': reverse_lazy('record_create',
                                    kwargs={
                                        'event_pk': self.event
                                    }),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Создать'))

        self.helper.add_input(Button(name='button',
                                     value='Закрыть',
                                     css_class='btn',
                                     hx_get=reverse_lazy('record_profile'),
                                     hx_target='#record-create-form',
                                     hx_swap="outerHTML"))

    @property
    def event(self):
        return self._event

    class Meta:
        model = Records
        fields = ('limit_clients', 'datetime')
        widgets = {
            'datetime': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'value': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                'min': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })
        }


class UpdateRecordForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'record-update-form'
        self.helper.attrs = {
            'hx-post': self.url_post,
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Изменить'))

        self.helper.add_input(Button(name='button',
                                     value='Отмена',
                                     css_class='btn',
                                     hx_get=reverse_lazy('record_profile',
                                                         kwargs={
                                                             'record_pk': self.instance.pk
                                                         }),
                                     hx_target='#record-update-form',
                                     hx_swap="outerHTML"))

    @property
    def url_post(self):
        url = reverse_lazy('record_update', kwargs={
                                                'record_pk': self.instance.pk
                                            })
        params = self.initial.get('params')
        self._url_pos = f'{url}?{params}'
        return self._url_pos

    class Meta:
        model = Records
        fields = ('limit_clients', 'datetime')
        widgets = {
            'datetime': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'value': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                'min': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })
        }
