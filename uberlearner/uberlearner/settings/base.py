from os.path import join, abspath, dirname

DEBUG = False
TEMPLATE_DEBUG = DEBUG

PROJECT_ROOT = abspath(join(dirname(__file__), '..', '..'))

ADMINS = (
    ('Uber Mailman', 'mailman@uberlearner.com'),
)

MANAGERS = ADMINS

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
MEDIA_ROOT = join(PROJECT_ROOT, '..', 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = join(PROJECT_ROOT, '..', 'collected-static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(PROJECT_ROOT, 'static'),
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
    #'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'uberlogger.middleware.ExceptionLoggerMiddleware',
)

ROOT_URLCONF = 'uberlearner.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'uberlearner.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(PROJECT_ROOT, 'templates'),
    #    "/home/abhin/djangoworkspace/uberlearner/uberlearner/templates/",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'main',
    'django.contrib.admin',
    'emailconfirmation',
    'allauth',
    'allauth.account',
    'bootstrap_toolkit',
    'captcha',
    'accounts',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'avatar',
    'easy_thumbnails',
    'tastypie',
    'courses',
    'courses.uberwidgets',
    'courses.uberwidgets.text',
    'filestorage',
    'south',
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
AUTH_PROFILE_MODULE = 'accounts.UserProfile'

# Avatar related settings
AVATAR_DEFAULT_SIZE = 150
AVATAR_MAX_AVATARS_PER_USER = 1
AVATAR_MAX_SIZE = 5 * 1024 * 1024 #5MB in bytes

# Add to TEMPLATE_CONTEXT_PROCESSORS and AUTHENTICATION_BACKENDS
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS, AUTHENTICATION_BACKENDS
TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
    'django.core.context_processors.debug',
    'allauth.context_processors.allauth',
    'allauth.account.context_processors.account',
)

INTERNAL_IPS = ('192.168.1.65', '127.0.0.1')

AUTHENTICATION_BACKENDS += (
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Amazon S3 storage settings
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_STORAGE_BUCKET_NAME = 'uberlearner'
# The current AWS_S3_CALLING_FORMAT is 'subdomain' and that is good enough for this

# Course related settings
COURSE_PHOTO_THUMB_SIZE = (80, 80)
COURSE_PHOTO_THUMB_QUALITY = 85
COURSE_PHOTO_THUMB_FORMAT = "JPEG"
THUMBNAIL_ALIASES = {
    '': {
        'thumbnail': {
            'size': (260, 189),
            'crop': 'smart'
        },
        'tile': {
            'size': (313, 227),
            'crop': 'smart'
        }
    }
}
THUMBNAIL_SUBDIR = 'thumbnails'

FILESTORAGE_ALLOWED_CONTENT_TYPES = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif']

LOGGLY_TOKEN = 'e86b110d-d51d-4570-91f5-f566a80ad6e2'