from django.core.exceptions import ValidationError
from tastypie.validation import Validation


class UberModelValidation(Validation):
    """
    Does validation of REST api data based on the model's full_clean method.
    """
    def __init__(self, **kwargs):
        print 'initializing'

    def is_valid(self, bundle, request=None):
        try:
            bundle.obj.full_clean()
        except ValidationError as ve:
            return ve.message_dict
        else:
            return {}