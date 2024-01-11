from allauth.account.adapter import DefaultAccountAdapter
from django.core.cache import cache


class MyCustomAccountAdapter(DefaultAccountAdapter):

    def login(self, request, user):
        super().login(request, user)
        session_key = self.request.session.session_key
        cache.set(session_key, user.pk, 60**2*12)

    def logout(self, request):
        session_key = self.request.session.session_key
        cache.delete(session_key)
        super().logout(request)

