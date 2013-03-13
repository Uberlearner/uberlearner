from django.conf import settings


def check_settings():
    """
    This method is to be run after the project settings file is loaded. It will check whether all the manual
    over-riding of the settings has been done by the user.
    """
    __REQUIRED_SECRET_NAMES__ = ['SECRET_KEY', 'RECAPTCHA_PUBLIC_KEY', 'RECAPTCHA_PRIVATE_KEY']

    for secret_name in __REQUIRED_SECRET_NAMES__:
        if not hasattr(settings, secret_name):
            raise Exception('Required setting {setting} was not found in the settings file'.format(setting=secret_name))
