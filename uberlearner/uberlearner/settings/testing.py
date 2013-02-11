import os
from base import *

DEBUG = True
TEMPLATE_DEBUG = True
TEST = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'uberlearner.db'),
    }
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

# TODO: switch this to local storage later
AWS_STORAGE_BUCKET_NAME = 'uberlearner-dev'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'