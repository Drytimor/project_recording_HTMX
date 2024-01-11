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
                                     hx_get=reverse_lazy('get_organization'),
                                     hx_target='#central-col',
                                     hx_swap="innerHTML"))

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
                                     hx_get=reverse_lazy('get_organization',
                                                         kwargs={
                                                             'pk': self.instance.pk
                                                         }),
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
                                        'pk': self.organization
                                    }),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',

        }
        self.helper.add_input(Submit(name='submit',
                                     value='Создать'))

        self.helper.add_input(Button(name='button',
                                     value='Закрыть',
                                     css_class='btn',
                                     hx_get=reverse_lazy('get_event'),
                                     hx_target='#event-create-form',
                                     hx_swap="outerHTML"))

    employees = forms.ModelMultipleChoiceField(queryset=Employees.objects.none(),
                                               widget=forms.CheckboxSelectMultiple)

    @property
    def organization(self):
        return self._organization

    class Meta:
        model = Events
        fields = ('name', 'employees')


class UpdateEventForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employees'].queryset = Employees.objects.filter(organization_id=self.instance.organization_id)
        self.helper = FormHelper(self)
        self._organization = self.initial['organization_id']
        self.helper.form_id = 'event-update-form'
        self.helper.attrs = {
            'hx-post': reverse_lazy('event_update', kwargs={
                'pk': self.instance.pk,
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
                                     hx_get=reverse_lazy('get_event',
                                                         kwargs={
                                                             'pk': self.instance.pk,
                                                             'org_pk': self.organization
                                                         }),
                                     hx_target='#event-update-form',
                                     hx_swap="outerHTML"))

    employees = forms.ModelMultipleChoiceField(queryset=Employees.objects.none(),
                                               widget=forms.CheckboxSelectMultiple)

    @property
    def organization(self):
        return self._organization

    class Meta:
        model = Events
        fields = ('name', 'employees')


class CreateEmployeeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self._organization = self.initial['organization_id']
        self.helper.form_id = 'employee-create-form'
        self.helper.attrs = {
            'hx-post': reverse_lazy('employee_create',
                                    kwargs={
                                        'pk': self.organization
                                    }),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Создать'))

        self.helper.add_input(Button(name='button',
                                     value='Закрыть',
                                     css_class='btn',
                                     hx_get=reverse_lazy('get_employee'),
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
                'pk': self.instance.pk,
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
                                     hx_get=reverse_lazy('get_employee',
                                                         kwargs={
                                                             'pk': self.instance.pk,
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
                                        'pk': self.event
                                    }),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Создать'))

        self.helper.add_input(Button(name='button',
                                     value='Закрыть',
                                     css_class='btn',
                                     hx_get=reverse_lazy('get_record'),
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
            'hx-post': reverse_lazy('record_update',
                                    kwargs={
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
                                     hx_get=reverse_lazy('get_record',
                                                         kwargs={
                                                             'pk': self.instance.pk
                                                         }),
                                     hx_target='#record-update-form',
                                     hx_swap="outerHTML"))

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
