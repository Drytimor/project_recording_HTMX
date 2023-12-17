from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button
from django import forms
from django.urls import reverse_lazy
from organization.models import Categories, Organizations, Employees, Events


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

    class Meta:
        model = Organizations
        fields = ('name', 'category')


class OrganizationUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'central-col'
        self.helper.attrs = {
            'hx-post': reverse_lazy('organization_update', kwargs={
                'pk': self.instance.pk
            }),
            'hx-target': '#org-profile',
            'hx-swap': 'outerHTML',
            'hx-select': '#org-profile'
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Изменить'))

        self.helper.add_input(Button(name='button',
                                     value='Отмена',
                                     css_class='btn',
                                     hx_get=reverse_lazy('organization_profile'),
                                     hx_target="#org-profile",
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
        self.helper.form_id = 'central-col'
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
                                     value='Отмена',
                                     css_class='btn',
                                     hx_get=reverse_lazy('events_list',
                                                         kwargs={
                                                             'pk': self.organization
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


class UpdateEventForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employees'].queryset = Employees.objects.filter(organization_id=self.instance.organization_id)
        self.helper = FormHelper(self)
        self.helper.form_id = 'central-col'
        self.helper.attrs = {
            'hx-post': reverse_lazy('event_update', kwargs={
                'pk': self.instance.pk,
            }),
            'hx-target': 'this',
            'hx-swap': 'outerHTML',
        }
        self.helper.add_input(Submit(name='submit',
                                     value='Изменить'))

        self.helper.add_input(Button(name='button',
                                     value='Отмена',
                                     css_class='btn',
                                     hx_get=reverse_lazy('events_list',
                                                         kwargs={
                                                             'pk': self.instance.organization_id
                                                         }),
                                     hx_target='#org-profile',
                                     hx_swap="innerHTML"))

    employees = forms.ModelMultipleChoiceField(queryset=Employees.objects.none(),
                                               widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Events
        fields = ('name', 'employees')


class CreateEmployeeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self._organization = self.initial['organization_id']
        self.helper.form_id = 'central-col'
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
                                     value='Отмена',
                                     css_class='btn',
                                     hx_get=reverse_lazy('employees_list',
                                                         kwargs={
                                                            'pk': self.organization
                                                         }),
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
                                     hx_get=reverse_lazy('employees_list',
                                                         kwargs={
                                                             'pk': self.instance.organization_id
                                                         }),
                                     hx_target='#org-profile',
                                     hx_swap="innerHTML"))

    class Meta:
        model = Employees
        fields = ('name',)