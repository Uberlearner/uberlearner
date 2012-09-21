from tastypie.authentication import SessionAuthentication

class UberAuthentication(SessionAuthentication):
    """
    Handles authentication for the course resources.
    """
    def is_authenticated(self, request, **kwargs):
        if request.method == 'GET':
            return True
        else:
            return super(UberAuthentication, self).is_authenticated(request, **kwargs)