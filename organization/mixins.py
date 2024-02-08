from django.core.paginator import Paginator, EmptyPage
from django.views.generic.base import TemplateResponseMixin
import os.path
from django.contrib import messages


class CustomMixin:
    organization_id = None
    employee_id = None
    event_id = None
    record_id = None
    user_id = None
    page_obj = None
    elided_page_range = None
    filter_form = None
    params = None

    def set_class_attributes_from_request(self):
        for attr, param in self.set_class_attributes_from_kwargs_request().items():
            setattr(self, attr, getattr(self, 'kwargs').get(param))

    def set_class_attributes_from_kwargs_request(self):
        attr = {}
        return attr

    def create_pagination(self, object_list, per_page=2, orphans=1,
                          on_each_side=1, on_ends=1):

        page_number = self.request.GET.get('page_number') or self.kwargs.get('page') or 1

        paginator = Paginator(object_list=object_list,
                              per_page=per_page,
                              orphans=orphans)
        page_obj = paginator.get_page(number=page_number)

        elided_page_range = paginator.get_elided_page_range(
            number=page_number,
            on_each_side=on_each_side,
            on_ends=on_ends
        )
        return page_obj, elided_page_range


class CustomTemplateResponseMixin(TemplateResponseMixin):
    response_htmx = False

    def render_to_response(self, context, **response_kwargs):

        """
        Return a response, using the `response_class` for this view, with a
        template rendered with the given context.

        Pass response_kwargs to the constructor of the response class.
        """
        if 'Hx-Request' in self.request.headers and self.response_htmx:
            path_list = self.template_name.split('/')
            self.template_name = os.path.join(path_list[0], 'htmx', path_list[1])
        response_kwargs.setdefault("content_type", self.content_type)
        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            using=self.template_engine,
            **response_kwargs,
        )



