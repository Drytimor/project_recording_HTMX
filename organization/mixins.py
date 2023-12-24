class CustomMixin:

    organization_id = None
    employee_id = None
    event_id = None

    def set_class_attributes_from_request(self):
        for attr, param in self.get_attr_from_request().items():
            setattr(self, attr, getattr(self, 'kwargs').get(param))

    def get_attr_from_request(self):
        attr = {}
        return attr



