from django.views.generic.base import TemplateResponseMixin, View, ContextMixin

from customer.services import get_organizations_all_from_db, get_events_all_from_db


# Create your views here.
class OrganizationsAll(TemplateResponseMixin, ContextMixin, View):

    template_name = 'organization_all.html'
    organizations = None

    def get(self, *args, **kwargs):
        self.organizations = get_organizations_all_from_db()
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.organizations:
            context['organizations_all'] = self.organizations
        return context


organizations_all = OrganizationsAll.as_view()


class EventsAll(TemplateResponseMixin, ContextMixin, View):

    template_name = 'event_all.html'
    events = None

    def get(self, *args, **kwargs):
        self.events = get_events_all_from_db()
        context = self.get_context_data()
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.events:
            context['events_all'] = self.events
        return context


events_all = EventsAll.as_view()
