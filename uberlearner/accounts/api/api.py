from avatar.templatetags.avatar_tags import avatar_url
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from tastypie import fields
from tastypie.resources import ModelResource
from accounts.models import UserProfile
from main.api.authentication import UberAuthentication
from main.api.serializers import UberSerializer

class UserResource(ModelResource):
    #profile = fields.ForeignKey('accounts.api.UserProfileResource', 'profile', full=True)
    class Meta:
        queryset = User.objects.all()
        authentication = UberAuthentication()
        #authorization = CourseAuthorization()
        resource_name = 'users'
        fields = ['username', 'first_name', 'last_name', 'last_login', 'profile']
        allowed_methods = ['get']
        include_absolute_url = True
        serializer = UberSerializer()

    def dehydrate(self, bundle):
        bundle.data['absolute_url'] = reverse('account_user_profile_with_username', kwargs={'username': bundle.obj.username})
        bundle.data['best_name'] = bundle.obj.profile.get_best_name()
        bundle.data['tiny_thumbnail'] = avatar_url(bundle.obj, size=settings.AVATAR_SIZE_IN_ENROLLMENTS_GRID)
        return bundle

class UserProfileResource(ModelResource):
    class Meta:
        queryset = UserProfile.objects.all()
        authentication = UberAuthentication()
        resource_name = 'profiles'
