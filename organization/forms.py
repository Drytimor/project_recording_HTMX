from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button
from django import forms
from django.urls import reverse_lazy

from organization.models import Categories, Organizations, Employees, Events


class CreateOrganizationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self._user = self.initial['user']
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

    @property
    def user(self):
        return self._user

    def save(self, commit=True):
        self.instance = super().save(commit=False)
        self.instance.save(user=self.user)

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

    class Meta:
        model = Organizations
        fields = ('name', 'category')
        widgets = {
            'category': forms.RadioSelect
        }


class CreateEventForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = self.initial['user']
        self.fields['employees'].queryset = self.user.employees.all()
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

    employees = forms.ModelMultipleChoiceField(queryset=Employees.objects.none(),
                                               widget=forms.CheckboxSelectMultiple)

    @property
    def user(self):
        return self._user

    def save(self, commit=True):
        self.instance = super().save(commit=False)
        # self.instance.save(user=self.user, employees=self.cleaned_data['employees'])
        employees = self.cleaned_data['employees']
        name = self.cleaned_data['name']
        event = self.user.events.create(name=name)
        event.employees.set(employees)

    class Meta:
        model = Events
        fields = ('name', 'employees')


class UpdateEventForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = self.initial['user']
        self.fields['employees'].queryset = self.user.employees.all()
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

    employees = forms.ModelMultipleChoiceField(queryset=Employees.objects.none(),
                                               widget=forms.CheckboxSelectMultiple)

    @property
    def user(self):
        return self._user

    class Meta:
        model = Events
        fields = ('name', 'employees')


class CreateEmployeeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self._user = self.initial['user']
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

    @property
    def user(self):
        return self._user

    def save(self, commit=True):
        self.instance = super().save(commit=False)
        # self.instance.save(user=self.initial['user'])
        name = self.cleaned_data['name']
        self.user.employees.create(name=name)

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