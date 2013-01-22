from django.conf import settings

# Email server settings
from django.core.urlresolvers import reverse_lazy

if settings.DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django_ses.SESBackend'
EMAIL_SUBJECT_PREFIX = "[Uberlearner] "
DEFAULT_FROM_EMAIL = 'abhin@uberlearner.com'

# Authentication and registration constants
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Uberlearner] "
ACCOUNT_UNIQUE_EMAIL = True
LOGIN_REDIRECT_URLNAME = "account_user_profile"
LOGIN_URLNAME = "account_login"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7
RECAPTCHA_PUBLIC_KEY = '6Ldk99ISAAAAAKBOZgQ8gyoaCKmHJ_2Pf-nhY4vv'
RECAPTCHA_PRIVATE_KEY = '6Ldk99ISAAAAALgZgEV1PKpGYlcoKl1x40taL4jO'
AUTH_PROFILE_MODULE = 'accounts.UserProfile'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = reverse_lazy('account_login')
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = reverse_lazy('account_user_profile')

# Avatar related settings
AVATAR_DEFAULT_SIZE = 150
AVATAR_MAX_AVATARS_PER_USER = 1
AVATAR_MAX_SIZE = 5 * 1024 * 1024 #5MB in bytes

TEMPLATE_CONTEXT_PROCESSORS = settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'allauth.account.context_processors.account',
    'allauth.socialaccount.context_processors.socialaccount',
)

AUTHENTICATION_BACKENDS = settings.AUTHENTICATION_BACKENDS + (
    'allauth.account.auth_backends.AuthenticationBackend',
)