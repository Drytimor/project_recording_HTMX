from django.contrib import admin
from .models import Organizations, Categories, Events, Employees

admin.site.register(Organizations)
admin.site.register(Categories)
admin.site.register(Events)
admin.site.register(Employees)
