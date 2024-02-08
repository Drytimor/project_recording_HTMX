from allauth.account.adapter import DefaultAccountAdapter
from django.core.cache import cache

from organization.services import _create_user_object_for_cache
from organization.tasks import tasks_set_user_object_from_cache, task_delete_object_from_cache


class MyCustomAccountAdapter(DefaultAccountAdapter):

    def login(self, request, user):
        super().login(request, user)
        user_object = _create_user_object_for_cache(user=user)
        tasks_set_user_object_from_cache(
            session_key=self.request.session.session_key,
            user_object=user_object
        )

    def logout(self, request):
        session_key = self.request.session.session_key
        task_delete_object_from_cache(cache_key=session_key)
        super().logout(request)

