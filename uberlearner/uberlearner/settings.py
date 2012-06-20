# Django settings for uberlearner project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Abhin Chhabra', 'chhabra.abhin@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'uberlearner',
        'USER': 'uberlearner',
        'PASSWORD': 'angelshit',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Edmonton'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/home/abhin/djangoworkspace/uberlearner/uberlearner/static/",
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '%30_ae&amp;ikyk2adxlykhdf4gjo4rfz!t9h(%n!b^06&amp;^u908dmc'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'uberlearner.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'uberlearner.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/home/abhin/djangoworkspace/uberlearner/uberlearner/templates/",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
    'django.contrib.admin',
    'emailconfirmation',
    'allauth',
    'allauth.account',
    'bootstrap_toolkit',
    'captcha',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Over-ride some of this behavious using settings_local.py
try:
    from uberlearner.settings_local import *
except ImportError:
    # settings_local.py has not been defined. That is all right.
    pass

# Email server settings
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django_ses.SESBackend'
EMAIL_SUBJECT_PREFIX = "[Uberlearner] "
AWS_ACCESS_KEY_ID = 'AKIAIYSEGJ5HLGMDPP2Q'
AWS_SECRET_ACCESS_KEY = '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'
DEFAULT_FROM_EMAIL = 'abhin@uberlearner.com'

# Authentication and registration constants
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Uberlearner] "
LOGIN_REDIRECT_URLNAME = "account_user_profile"
EMAIL_CONFIRMATION_DAYS = 7
RECAPTCHA_PUBLIC_KEY = '6Ldk99ISAAAAAKBOZgQ8gyoaCKmHJ_2Pf-nhY4vv'
RECAPTCHA_PRIVATE_KEY = '6Ldk99ISAAAAALgZgEV1PKpGYlcoKl1x40taL4jO'

# Add to TEMPLATE_CONTEXT_PROCESSORS and AUTHENTICATION_BACKENDS
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS, AUTHENTICATION_BACKENDS
TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
    'allauth.context_processors.allauth',
    'allauth.account.context_processors.account', 
)

AUTHENTICATION_BACKENDS += (
    'allauth.account.auth_backends.AuthenticationBackend',
)

