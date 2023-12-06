from django.contrib import admin

from .models import User, Organizations, Categories

admin.site.register(User)
admin.site.register(Organizations)
admin.site.register(Categories)
