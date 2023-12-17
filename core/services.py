from .models import User
from django.db import transaction


@transaction.atomic
def update_user_from_db(user, form):
    data = form.cleaned_data
    User.objects.filter(id=user.pk).update(**data)


@transaction.atomic
def delete_user_from_db(user):
    user.delete()
