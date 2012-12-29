from base import *
import os

DEBUG = False
TEMPLATE_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'uberlearner.db'),
    }
}

LOGGING_ROOT = os.path.join(PROJECT_ROOT, '..', 'log')

LOGGING = {
    'version': 1,
    'disable_existing_loggirs': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    'handlers': {
        'errors': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(LOGGING_ROOT, 'errors.log'),
        },
    },
    'loggers': {
        'errors': {
            'handlers': ['errors'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}