import factory
from django.contrib.auth.models import User


class UserFactory(factory.Factory):
    FACTORY_FOR = User

    first_name = 'Test'
    last_name = 'User'
    username = factory.Sequence(lambda n: "testuser{0}".format(n))
    email = 'testuser@example.com'
    password = 'aoeuaoeu'
    _plain_text_password = 'aoeuaoeu'

    is_staff = False
    is_active = True
    is_superuser = False

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()

        return user