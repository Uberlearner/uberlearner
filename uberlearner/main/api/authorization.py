from django.conf import settings
from django.core.urlresolvers import resolve
from django.core.exceptions import ObjectDoesNotExist
from tastypie.authorization import Authorization


class UberAuthorization(Authorization):
    def get_object(self, path, object_class=None):
        try:
            pk = resolve(path)[2]['pk']
        except (IndexError, KeyError):
            object = None
        else:
            try:
                object_class = object_class or self.resource_meta.object_class
                object = object_class.objects.get(pk=pk)
            except ObjectDoesNotExist:
                object = None
        return object