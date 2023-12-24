from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button
from django import forms
from django.urls import reverse_lazy
from organization.models import Categories, Organizations, Employees, Events, EventRecords


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
                                     hx_get=reverse_lazy('organization_profile'),
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
                                     hx_get=reverse_lazy('organization_profile'),
                                     hx_target="#org-profile",
                                     hx_select='#org-profile',
                                     hx_swap="innerHTML"))

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
                                     css_id='btn_delete_form_event',
                                     hx_target='#org-profile',
                                     hx_swap="innerHTML"))

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
                                     hx_get=reverse_lazy('event_profile',
                                                         kwargs={
                                                             'pk': self.instance.pk,
                                                             'org_pk': self.organization
                                                         }),
                                     hx_target='#org-profile',
                                     hx_swap="innerHTML"))

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
                                     css_id='btn_delete_form_emp',
                                     hx_target='#org-profile',
                                     hx_swap="innerHTML"))

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
                                     hx_get=reverse_lazy('employee_profile',
                                                         kwargs={
                                                             'pk': self.instance.pk,
                                                             'org_pk': self.organization
                                                         }),
                                     hx_target='#org-profile',
                                     hx_select='#org-profile',
                                     hx_swap="innerHTML"))

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

    datetime = forms.SplitDateTimeField(widget=forms.SplitDateTimeWidget(date_attrs={'type': 'date'},
                                                                         time_attrs={'type': 'time'}))

    @property
    def event(self):
        return self._event

    class Meta:
        model = EventRecords
        fields = ('datetime', 'limit_clients')
