import factory
from django.contrib.auth.models import User

class UserFactory(factory.Factory):
    FACTORY_FOR = User

    first_name = 'Test'
    last_name = 'User'
    username = factory.Sequence(lambda n: "testuser{0}".format(n))
    email = 'testuser@example.com'
    password = 'aoeuaoeu'

    is_staff = False
    is_active = True
    is_superuser = False