from tastypie.resources import ModelResource
from authentication import UberAuthentication
from serializers import UberSerializer


class UberModelResource(ModelResource):
    class Meta:
        authentication = UberAuthentication()
        serializer = UberSerializer()
