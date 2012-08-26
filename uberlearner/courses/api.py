from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import Authorization
from courses.models import Course
from django.contrib.auth.models import User              
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.serializers import Serializer
from tastypie.utils.timezone import make_naive
from django.utils import dateformat, timezone
from django.utils import timezone

class UberSerializer(Serializer):
    def format_datetime(self, data):
        data = make_naive(data)
        today = make_naive(timezone.now())
        time_string = dateformat.time_format(data, "P")
        date_string = dateformat.format(data, "j M Y") 
        if data.date() == today.date():
            return "today, " + time_string
        else:
            return date_string

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name', 'last_login']
        allowed_methods = ['get']
        include_absolute_url = True

class CourseResource(ModelResource):
    instructor = fields.ForeignKey(UserResource, 'instructor', full=True)
    title = fields.CharField(attribute='title')
    
    class Meta:
        queryset = Course.objects.filter(is_public=True)
        resource_name = 'course'
        allowed_methods = ['get']
        authentication = SessionAuthentication()
        limit = 10
        ordering = ['title', 'popularity', 'instructor', 'creation_timestamp']
        filtering = {
            "instructor": ALL_WITH_RELATIONS,
        }
        serializer = UberSerializer()
        include_absolute_url = True
        
    def is_authenticated(self, request, **kwargs):
        """
        The user doesn't need to be authenticated to view the courses. For everything else,
        we use session authentication.
        """
        if request.method == 'GET':
            return True
        return super(CourseResource, self).is_authenticated(request, **kwargs)
    
    def is_authorized(self, request, object=None):
        """
        If the user just wants to read the database, then allow this to happen. The filtering
        of the private courses will take place in the apply_authorization_limits method.
        """
        if request.method == 'GET':
            return True
        return super(CourseResource, self).is_authorized(request, object)
    
    def apply_filters(self, request, applicable_filters):
        # if the filters list has instructor, then modify its value to be the actual user
        if 'instructor__exact' in applicable_filters:
            instructor_username = applicable_filters['instructor__exact'] 
            if isinstance(instructor_username, basestring):
                applicable_filters['instructor__exact'] = User.objects.get(username=instructor_username)
        
        result = super(CourseResource, self).apply_filters(request, applicable_filters)
        return result
    
#    def apply_authorization_limits(self, request, object_list):
#        """
#        If the user is not the author of a private course, then the user cannot access it.
#        """
#        authorized_objects = super(CourseResource, self).apply_authorization_limits(request, object_list)
#        def filter_private_courses(course):
#            if isinstance(course, Course):
#                return course.is_public or course.instructor == request.user
#            return False
#        return filter(filter_private_courses, authorized_objects)
