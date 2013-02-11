from tastypie.authentication import SessionAuthentication, BasicAuthentication
from django.conf import settings

class UberAuthentication(SessionAuthentication):
    """
    Handles authentication for the course resources.
    """
    def is_authenticated(self, request, **kwargs):
        if request.method == 'GET':
            return True
        else:
            return super(UberAuthentication, self).is_authenticated(request, **kwargs)

if getattr(settings, 'TEST') and settings.TEST:
    UberAuthentication = BasicAuthentication