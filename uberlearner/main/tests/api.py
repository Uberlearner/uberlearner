from tastypie.test import ResourceTestCase
from accounts.tests.factories import UserFactory


class UberResourceTestCase(ResourceTestCase):
    class Meta:
        # The model being tested
        model = None
        # The default data to use when creating objects
        post_data = {}
        # The uri endpoint for the list of objects of type model
        list_uri = None

    def __init__(self, *args, **kwargs):
        self._meta = self.Meta()
        super(UberResourceTestCase, self).__init__(*args, **kwargs)

    def _get_credentials(self, user):
        """
        Create credentials from a user object

        :param user: instance of model User
        :return: String
        """
        return self.create_basic(user.username, UserFactory._plain_text_password)

    def _http_method(self, method=None, **kwargs):
        """
        Makes an HTTP request based on the method string.

        :param method: One of {'get', 'post', 'put', 'delete', 'patch'}
        :param kwargs: The arguments to pass to the function corresponding to the http method in the client.
        :return: :raise:
        """
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
        """
        Makes an HTTP POST request

        :param data: The data to attach to the request
        :param kwargs: The arguments to pass to the method in the test client
        :return:
        """
        data = data or self._meta.post_data
        return self._http_method(method='post', uri=self._meta.list_uri, data=data, **kwargs)

    def _read(self, obj, **kwargs):
        """
        Makes an HTTP GET request on the given object

        :param obj: The data to attach to the request
        :param kwargs: The arguments to pass to the method in the test client
        :return:
        """
        if 'uri' in kwargs:
            del kwargs['uri']
        return self._http_method(method='get', uri=obj.get_resource_uri(), **kwargs)

    def _read_list(self, **kwargs):
        """
        Makes a GET request at the list url endpoint

        :param kwargs: The arguments to pass to the method in the test client
        :return:
        """
        if 'uri' in kwargs:
            del kwargs['uri']
        return self._http_method(method='get', uri=self._meta.list_uri, **kwargs)

    def _update(self, obj, data_update={}, **kwargs):
        """
        Makes an HTTP PUT request on the given object

        :param obj: The data to attach to the request
        :param data_update: A dictionary containing the update data
        :param kwargs: The arguments to pass to the method in the test client
        :return:
        """
        if 'uri' in kwargs:
            del kwargs['uri']
        if 'data' in kwargs:
            del kwargs['data']
        return self._http_method(method='put', uri=obj.get_resource_uri(), data=data_update, **kwargs)

    def _delete(self, obj, **kwargs):
        """
        Makes an HTTP DELETE reqeust on the given object

        :param obj: The data to attach to the request
        :param kwargs: The arguments to pass to the method in the test client
        :return:
        """
        if 'uri' in kwargs:
            del kwargs['uri']
        return self._http_method(method='delete', uri=obj.get_resource_uri(), **kwargs)

    def _test_packet_attributes(self, packet, white_list, black_list):
        """
        Tests a given packet to confirm that:
        1) All the items in the white_list are present in the packet
        2) None of the items in the black_list are present in the packet
        3) All of the keys in the packet dictionary are present in the white_list

        :param packet: A dictionary that represents the packet
        :param white_list: A list of the keys that should be present in the packet
        :param black_list: A list of the keys that should not be present in the packet
        """
        self.assertEqual(len(frozenset(white_list).intersection(frozenset(black_list))), 0,
                         msg='The white_list and black_list cannot have common values')

        for legal_item in white_list:
            self.assertIn(legal_item, packet)
        for illegal_item in black_list:
            self.assertNotIn(illegal_item, packet)

        # and now we iterate through the keys in the packet to confirm that they exist
        # in the white_list. This whole operation (along with checking the other way around)
        # was not done using a set equals because we want the test to fail with an appropriate
        # fail message indicating exactly what went wrong
        for key in packet.keys():
            self.assertIn(key, white_list)