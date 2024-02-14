from typing import Iterable

from django.contrib.postgres.aggregates import BoolOr
from django.db.models import QuerySet, Prefetch, Q
from django.http import QueryDict
from django_filters import MultipleChoiceFilter, FilterSet, ChoiceFilter, DateFilter
import datetime
from allauth_app.settings import CACHE_KEY_ALL_OBJECT_FROM_DB, CACHE_KEY_MODEL_OBJECT_ID, CACHE_KEY_USER_ASSIGNED_EVENTS
from django.core.cache import cache
from django.forms import widgets

from customer.models import Recordings, AssignedEvents
from organization.models import (
    Organizations, CategoriesChoices, Events, PaymentTariffChoices, StatusOpeningChoices, Records, Employees)


def _create_filtered_object(queryset: QuerySet, data: QueryDict,
                            filter_class, filter_name=None):

    filter_objects = filter_class(queryset=queryset,
                                  data=data,
                                  filter_name=filter_name)
    filtered_queryset = filter_objects.qs
    filter_form = filter_objects.form

    return filtered_queryset, filter_form


class EventsFilter(FilterSet):

    def __init__(self, data=None, queryset=None, filter_name=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        self.filter_name = filter_name

    tariff = MultipleChoiceFilter(field_name='status_tariff',
                                  label='вход',
                                  widget=widgets.CheckboxSelectMultiple,
                                  choices=PaymentTariffChoices.choices)

    category = MultipleChoiceFilter(field_name='organization__category__name',
                                    label='категория',
                                    widget=widgets.CheckboxSelectMultiple,
                                    choices=CategoriesChoices.choices)

    def get_filter_queryset_from_cache(self, queryset, filter_name):

        unique_cache_key_queryset = CACHE_KEY_MODEL_OBJECT_ID
        timeout_from_cache = 60*2

        filtered_queryset = cache.get(key=filter_name)

        if filtered_queryset is None:

            filtered_queryset = self.filter_queryset(queryset=queryset)

            cache.set(key=filter_name,
                      value=filtered_queryset,
                      timeout=timeout_from_cache)

            cache.set_many({unique_cache_key_queryset.format(model_name=_object.__class__.__name__,
                                                             object_id=_object.id): _object for _object in queryset},
                           timeout=timeout_from_cache)

        list_objects_from_cache = cache.get_many(
            keys=[unique_cache_key_queryset.format(model_name=_object.__class__.__name__,
                                                   object_id=_object.id) for _object in filtered_queryset]
        ).values()

        return list(list_objects_from_cache)

    @property
    def qs(self):
        if not hasattr(self, "_qs"):
            qs = self.queryset
            if self.is_bound:
                # ensure form validation before filtering
                self.errors
                qs = self.get_filter_queryset_from_cache(
                    queryset=qs, filter_name=self.filter_name) if self.filter_name else self.filter_queryset(qs)
            self._qs = qs
        return self._qs

    class Meta:
        model = Events
        fields = [
            'tariff',
            'category'
        ]


# Organization
class OrganizationFilter(EventsFilter):

    category = MultipleChoiceFilter(field_name='category__name',
                                    label='категория',
                                    widget=widgets.CheckboxSelectMultiple,
                                    choices=CategoriesChoices.choices)
    tariff = ...

    class Meta:
        model = Organizations
        fields = [
            'category'
        ]


def _get_organizations_all_from_cache():
    cache_key_organization_all = CACHE_KEY_ALL_OBJECT_FROM_DB.format(model='Organizations')
    organizations_all = cache.get(cache_key_organization_all)
    return organizations_all


def _get_organizations_all_from_db():
    organizations_all = Organizations.objects.select_related('category')
    return organizations_all


def _get_organization_object_from_db(organization_id: int):
    organization = Organizations.objects.select_related('category').get(id=organization_id)
    return organization


# Event
class EventsListUserFilter(EventsFilter):
    ...


def _get_events_all_from_cache():
    cache_key_events_all = CACHE_KEY_ALL_OBJECT_FROM_DB.format(model='Events')
    events = cache.get(cache_key_events_all)
    return events


def _get_events_all_from_db():
    events = Events.objects.select_related('organization')
    return events


def _get_organization_events_from_db(organization_id: int):
    organization_events = Events.objects.filter(organization_id=organization_id)
    return organization_events


def _get_user_events_id_from_db(user_id):

    user_events_id = (
        Recordings.objects.values_list('record__events__id')
                          .filter(user_id=user_id))
    return user_events_id


def _get_assigned_user_events_from_cache(user_id: int):

    cache_key_user_assigned_events = CACHE_KEY_USER_ASSIGNED_EVENTS.format(user_id=user_id)
    assigned_user_events = cache.get(key=cache_key_user_assigned_events)

    return assigned_user_events


def _get_user_events_and_assigned_user_events_from_db(events_id: Iterable, assigned_events_id: Iterable):

    user_events = (
        Events.objects.select_related('organization')
                      .prefetch_related(
                            Prefetch('employees', to_attr='employees_event')
                            )
                      .filter(Q(id__in=events_id) | Q(id__in=assigned_events_id)))
    return user_events


def _get_user_events_with_assigned_field_for_profile(user_id: int):

    user_events = (
        Events.objects.select_related('organization')
                      .prefetch_related(
                          Prefetch('employees', to_attr='employees_event')
                      ).filter(
            Q(records__recordings__user=user_id) | Q(assigned_events__user=user_id)
        ).annotate(
            assigned=BoolOr(Q(assigned_events__user=user_id)))
        )
    return user_events


def _get_assigned_user_events_from_db(user_id: int):

    assigned_user_events = (
        AssignedEvents.objects.filter(user_id=user_id)
                              .values_list('event', 'user'))
    return assigned_user_events


def _get_event_card_from_db(event_id: int):

    event = (
        Events.objects.filter(id=event_id).prefetch_related(
            Prefetch(lookup='employees', to_attr='event_employees')
        ).get()
    )
    return event
# Employees


# Record
class RecordsListUserFilter(FilterSet):

    def __init__(self, data=None, queryset=None, filter_name=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        self.filter_name = filter_name

    status_opening = ChoiceFilter(field_name='status_opening',
                                  label='Статус',
                                  widget=widgets.Select,
                                  choices=StatusOpeningChoices.choices)

    datetime = DateFilter(field_name='datetime',
                          lookup_expr='date',
                          label='Дата',
                          widget=widgets.DateInput(attrs={
                                    'type': 'date',
                                    'value': datetime.date.today().strftime("%Y-%m-%d"),
                                    'min': datetime.date.today().strftime("%Y-%m-%d")
                                }))

    def get_filter_queryset_from_cache(self, queryset, filter_name):

        unique_cache_key_queryset = CACHE_KEY_MODEL_OBJECT_ID
        timeout_from_cache = 60*5

        filtered_queryset_from_cache = cache.get_or_set(key=filter_name,
                                                        default=self.filter_queryset(queryset=queryset),
                                                        timeout=timeout_from_cache)

        list_objects_from_cache = cache.get_many(
                keys=[unique_cache_key_queryset.format(model_name=_object.__class__.__name__,
                                                       object_id=_object.id) for _object in filtered_queryset_from_cache]
            ).values()

        if not list_objects_from_cache:

            cache.set_many({unique_cache_key_queryset.format(model_name=_object.__class__.__name__,
                                                             object_id=_object.id): _object for _object in queryset},
                           timeout=timeout_from_cache)

            list_objects_from_cache = cache.get_many(
                    keys=[unique_cache_key_queryset.format(model_name=_object.__class__.__name__,
                                                           object_id=_object.id) for _object in filtered_queryset_from_cache]
                ).values()

        return list(list_objects_from_cache)

    @property
    def qs(self):
        if not hasattr(self, "_qs"):
            qs = self.queryset
            if self.is_bound:
                # ensure form validation before filtering
                self.errors
                qs = self.get_filter_queryset_from_cache(queryset=qs,
                                                         filter_name=self.filter_name) if self.filter_name else self.filter_queryset(qs)
            self._qs = qs
        return self._qs

    class Meta:
        model = Records
        fields = [
            'datetime',
            'status_opening'
        ]


class EventRecordsListFilter(RecordsListUserFilter):
    ...


class UserRecordsInEventFilter(FilterSet):

    def __init__(self, data=None, queryset=None, filter_name=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        self.filter_name = filter_name

    status_opening = ChoiceFilter(field_name='status_opening',
                                  label='Статус',
                                  widget=widgets.Select,
                                  choices=StatusOpeningChoices.choices)

    datetime = DateFilter(field_name='datetime',
                          lookup_expr='date',
                          label='Дата',
                          widget=widgets.DateInput(attrs={
                                    'type': 'date',
                                    'value': datetime.date.today().strftime("%Y-%m-%d"),
                                    'min': datetime.date.today().strftime("%Y-%m-%d")
                                }))

    class Meta:
        model = Records
        fields = [
            'datetime',
            'status_opening'
        ]


def _get_record_object_from_db(record_id: int):

    record = Records.objects.get(id=record_id)
    return record


def _get_user_records_in_event_from_db(event_id: int, user_id: int):

    records_user = (
        Records.objects.filter(recordings__user=user_id, events=event_id)
    )
    return records_user


def _get_event_records_with_registered_user_field(event_id: int, user_id: int):

    event_records = (
        Records.objects.filter(events=event_id)
                       .annotate(registered_user=BoolOr(Q(recordings__user=user_id)))
    )
    return event_records


def _get_event_records(event_id: int):

    event_records = (
        Records.objects.filter(events=event_id)
    )
    return event_records



