from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models.query_utils import Q
from tastypie.bundle import Bundle
from tastypie.http import HttpGone, HttpMultipleChoices
from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import Authorization
from tastypie.utils.urls import trailing_slash
from courses.models import Course, Instructor, Page
from django.contrib.auth.models import User              
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.serializers import Serializer
from tastypie.utils.timezone import make_naive
from django.utils import dateformat, timezone
from django.core.urlresolvers import reverse

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

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'users'
        fields = ['username', 'first_name', 'last_name', 'last_login']
        allowed_methods = ['get']
        include_absolute_url = True
        
    def dehydrate(self, bundle):
        bundle.data['absolute_url'] = reverse('course.by_user', kwargs={'username': bundle.obj.username})
        return bundle

class PubliclyViewableMixin(object):
    """
    This mixin encapsulates the behaviour of resources that want to be publicly viewable. The class
    that uses this mixin can later decide whether it would like to add restrictions like not allowing
    private courses to be viewed by over-riding the apply_authorization_limits method.
    """
    def is_authenticated(self, request, **kwargs):
        """
        The user doesn't need to be authenticated to view. For everything else, we
        use session authentication
        """
        if request.method == 'GET':
            return True
        return super(PubliclyViewableMixin, self).is_authenticated(request, **kwargs)

    def is_authorized(self, request, object=None):
        """
        If the user just wants to read the database, then allow this to happen. The filtering
        of the private objects will take place in the apply_authorization_limits method.
        """
        if request.method == 'GET':
            return True
        return super(PubliclyViewableMixin, self).is_authorized(request, object)

class PageResource(PubliclyViewableMixin, ModelResource):
    class Meta:
        queryset = Page.objects.all()
        resource_name = 'pages'

    def apply_authorization_limits(self, request, object_list):
        """
        If the user is not the author of the course and the course is private, then the user cannot
        access the course (unless of course they are a superuser).
        """
        authorized_objects = super(PageResource, self).apply_authorization_limits(request, object_list)
        def filter_private_courses(page):
            if isinstance(page, Page):
                course = page.course
                return course.is_public or request.user == course.instructor or request.user.is_superuser
            return False
        return filter(filter_private_courses, authorized_objects)

    def obj_get(self, request=None, **kwargs):
        """
        Technically it is not required to use the course to find a unique page. But for emphasizing that
        a page belongs to a course in the scheme of things, it is being made a sub-resource of course.
        In that case, it is for integrity of the resource model that we are confirming that the course
        is indeed the parent of the page.
        """
        page_id = kwargs.get('page_id')
        course = kwargs.get('course')
        return Page.objects.get(pk=page_id, course=course)

    def get_resource_uri(self, bundle_or_obj=None, url_name='api_dispatch_list'):
        from uberlearner.urls import v1_api

        if not bundle_or_obj:
            return u''

        if isinstance(bundle_or_obj, Bundle):
            course_id = bundle_or_obj.obj.course.id
            page_id = bundle_or_obj.data['id']
        else:
            course_id = bundle_or_obj.course.id
            page_id = bundle_or_obj.id

        resource_uri = reverse('api_get_page', kwargs={
            'pk': course_id,
            'page_id': page_id,
            'resource_name': CourseResource._meta.resource_name,
            'api_name': v1_api.api_name
        })
        return resource_uri

class CourseResource(PubliclyViewableMixin, ModelResource):
    instructor = fields.ForeignKey(UserResource, 'instructor', full=True)
    title = fields.CharField(attribute='title')
    pages = fields.OneToManyField(PageResource, 'pages', full=True)
    
    class Meta:
        queryset = Course.objects.all()
        resource_name = 'courses'
        allowed_methods = ['get']
        authentication = SessionAuthentication()
        limit = 10
        ordering = ['title', 'popularity', 'instructor', 'creation_timestamp']
        filtering = {
            "instructor": ALL_WITH_RELATIONS,
        }
        serializer = UberSerializer()
        include_absolute_url = True

    def prepend_urls(self):
        """
        Page resource is a sub-resource of course.
        """
        return [
            url(r'^(?P<resource_name>{0})/(?P<pk>\w[\w/-]*)/{1}/(?P<page_id>\d+){2}$'.format(
                self._meta.resource_name, PageResource._meta.resource_name, trailing_slash()
            ), self.wrap_view('get_page'), name='api_get_page'),
        ]

    def get_page(self, request, **kwargs):
        """
        The view that backs the page resource inside of the course resource.
        """
        page_id = kwargs.pop('page_id')
        try:
            course = self.cached_obj_get(request=request, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices('More than one resource is found at this URI')

        page_resource = PageResource()
        return page_resource.get_detail(request, page_id=page_id, course=course)

    def apply_filters(self, request, applicable_filters):
        # if the filters list has instructor, then modify its value to be the actual user
        if 'instructor__exact' in applicable_filters:
            instructor_username = applicable_filters['instructor__exact'] 
            if isinstance(instructor_username, basestring):
                applicable_filters['instructor__exact'] = Instructor.objects.get(user__username=instructor_username)
        
        result = super(CourseResource, self).apply_filters(request, applicable_filters)
        return result
    
    def apply_authorization_limits(self, request, object_list):
        """
        If the user is not the author of a private course, then the user cannot access it (unless
        of course he/she is a super-user).
        """
        authorized_objects = super(CourseResource, self).apply_authorization_limits(request, object_list)
        if request.user.is_superuser:
            return authorized_objects
        else:
            return authorized_objects.filter(Q(is_public=True) | Q(instructor=request.user.id))

    def dehydrate_pages(self, bundle):
        if 'pages' in bundle.data and isinstance(bundle.data['pages'], list):
            for page in bundle.data['pages']:
                if 'html' in page.data:
                    page.data.pop('html')
            return bundle.data['pages']