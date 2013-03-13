import os
from base import *

DEBUG = True
TEMPLATE_DEBUG = True

INTERNAL_IPS = ('127.0.0.1', )

SECRET_KEY = '%30_ae&amp;ikyk2adxlykhdf4gjo4rfz!t9h(%n!b^06&amp;^u908dmc'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'uberlearner.db'),
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

try:
    from development_local import *
except ImportError:
    print 'Attempted to import development_local failed. Expect this to be the cause of your woes.'