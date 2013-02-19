from tastypie.test import ResourceTestCase
from accounts.tests.factories import UserFactory


class UberResourceTestCase(ResourceTestCase):
    class Meta:
        model = None
        post_data = {}
        list_uri = None

    def __init__(self, *args, **kwargs):
        self._meta = self.Meta()
        super(UberResourceTestCase, self).__init__(*args, **kwargs)

    def _get_credentials(self, user):
        return self.create_basic(user.username, UserFactory._plain_text_password)

    def _http_method(self, method=None, **kwargs):
        if method is None:
            raise ValueError('Some action has to be performed on the endpoint')
        if not hasattr(self.api_client, method):
            raise ValueError('Illegal http method attempted on the endpoint')

        if 'authentication' in kwargs and kwargs['authentication'] is not None:
            kwargs['authentication'] = self._get_credentials(kwargs['authentication'])

        pre_creation_count = self._meta.model.objects.count()
        response = getattr(self.api_client, method)(**kwargs)
        post_creation_count = self._meta.model.objects.count()

        return response, pre_creation_count, post_creation_count

    def _create(self, data=None, **kwargs):
        data = data or self._meta.post_data
        return self._http_method(method='post', uri=self._meta.list_uri, data=data, **kwargs)

    def _read(self, obj, **kwargs):
        if 'uri' in kwargs:
            del kwargs['uri']
        return self._http_method(method='get', uri=obj.get_resource_uri(), **kwargs)

    def _read_list(self, **kwargs):
        if 'uri' in kwargs:
            del kwargs['uri']
        return self._http_method(method='get', uri=self._meta.list_uri, **kwargs)

    def _update(self, obj, data_update={}, **kwargs):
        if 'uri' in kwargs:
            del kwargs['uri']
        if 'data' in kwargs:
            del kwargs['data']
        return self._http_method(method='put', uri=obj.get_resource_uri(), data=data_update, **kwargs)

    def _delete(self, obj, **kwargs):
        if 'uri' in kwargs:
            del kwargs['uri']
        return self._http_method(method='delete', uri=obj.get_resource_uri(), **kwargs)
