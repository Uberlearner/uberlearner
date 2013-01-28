from tastypie.utils.timezone import make_naive
from django.utils import dateformat, timezone

try:
    from tastypie_camelcase.serializers import CamelCaseJSONSerializer as Serializer
except ImportError:
    from tastypie.serializers import Serializer

class UberSerializer(Serializer):
    """
    Over-rides the serialization behaviour of the default serializer for datetime objects.
    """
    def format_datetime(self, data):
        data = make_naive(data)
        today = make_naive(timezone.now())
        time_string = dateformat.time_format(data, "P")
        date_string = dateformat.format(data, "j M Y")
        if data.date() == today.date():
            return "today, " + time_string
        else:
            return date_string