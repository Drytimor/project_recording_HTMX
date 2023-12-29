from django.views.generic.base import TemplateResponseMixin
import os.path


class CustomMixin:

    organization_id = None
    employee_id = None
    event_id = None
    record_id = None
    user_id = None

    def set_class_attributes_from_request(self):
        for attr, param in self.get_attr_from_request().items():
            setattr(self, attr, getattr(self, 'kwargs').get(param))

    def get_attr_from_request(self):
        attr = {}
        return attr


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
            headers=self.set_headers_to_response(),
            **response_kwargs,
        )

    def set_headers_to_response(self):
        headers = {}
        return headers

