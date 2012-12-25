from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models.query_utils import Q
from django.http import HttpResponse
from easy_thumbnails.files import get_thumbnailer
from tastypie.authentication import Authentication
from tastypie.exceptions import ImmediateHttpResponse, BadRequest
from tastypie.http import HttpGone, HttpMultipleChoices, HttpNoContent, HttpForbidden
from tastypie.resources import ModelResource, convert_post_to_patch
from tastypie import fields, http
from tastypie.utils import trailing_slash
from courses.api.authentication import UberAuthentication
from courses.api.authorization import UberAuthorization
from courses.api.serializers import UberSerializer
from courses.models import Course, Instructor, Page, Enrollment
from django.contrib.auth.models import User              
from tastypie.constants import ALL_WITH_RELATIONS
from django.core.urlresolvers import reverse
import time

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        authentication = UberAuthentication()
        authorization = UberAuthorization()
        resource_name = 'users'
        fields = ['username', 'first_name', 'last_name', 'last_login']
        allowed_methods = ['get']
        include_absolute_url = True
        serializer = UberSerializer()
        
    def dehydrate(self, bundle):
        bundle.data['absolute_url'] = reverse('course.by_user', kwargs={'username': bundle.obj.username})
        return bundle

class PageResource(ModelResource):
    class Meta:
        queryset = Page.objects.all()
        authentication = Authentication()
        #authorization = UberAuthorization()
        resource_name = 'pages'
        serializer = UberSerializer()
        allowed_methods = ['get', 'put', 'post', 'patch', 'delete']
        always_return_data = True

    def obj_create(self, bundle, request=None, **kwargs):
        course_id = bundle.data['course_id']
        if not kwargs:
            kwargs = {}
        kwargs.update({'course_id': course_id})
        created = super(PageResource, self).obj_create(bundle, request, **kwargs)
        return created

    def obj_update(self, bundle, request=None, skip_errors=False, **kwargs):
        # because of a bug in tastypie, the is_authorized method doesn't have access to the page object.
        # This means that permission handling will have to be done elsewhere. This is one of those methods.
        # TODO: FIXME:
        # I know this is a horrible way to do it because it involves a wasted database lookup but this will
        # be improved upon later. (maybe through the use of cached_obj_get)
        if 'pk' in kwargs:
            page = Page.objects.get(pk=kwargs['pk'])
            if page.course.instructor != request.user and not request.user.is_superuser:
                raise ImmediateHttpResponse(response=http.HttpUnauthorized())
        return super(PageResource, self).obj_update(bundle, request, skip_errors, **kwargs)

    def patch_list(self, request, **kwargs):
        """
        This is usually used by the client to change the order of pages. As such, the checks performed here
        are:
        1. Whether all the pages belong to the same course
        2. Whether the current user has write access to the course.
        """
        # even though this is inefficient, we have to execute a couple of lines from the super.patch_list method to
        # get the deserialized version of the request. This will be removed if tastypie fixes the authorization problem
        # (where the is_authorized method doesn't provide access to the object)
        post_request = convert_post_to_patch(request)
        deserialized = self.deserialize(post_request, post_request.raw_post_data, format=post_request.META.get('CONTENT_TYPE', 'application/json'))
        if "objects" not in deserialized:
            raise BadRequest("Invalid data sent.")
        q_expression = None
        for data in deserialized['objects']:
            if not q_expression:
                q_expression = Q(id=data['id'])
            else:
                q_expression |= Q(id=data['id'])
        pages = Page.objects.filter(q_expression)
        current_course = None
        for page in pages:
            if not current_course:
                current_course = page.course
            elif page.course != current_course:
                raise BadRequest("List patch cannot be applied to pages from different courses")
            elif page.course.instructor != request.user and not request.user.is_superuser:
                raise PermissionDenied("Only the author of the course or the super-user can apply list patch to pages")
        patched = super(PageResource, self).patch_list(request, **kwargs)
        return patched

    def delete_detail(self, request, **kwargs):
        """
        When the client wants to delete a user, we have to check whether the user is a superuser or the owner
        of the page before allowing this to happen.
        """
        page = self.obj_get(request, **self.remove_api_resource_names(kwargs))
        if request.user != page.course.instructor and not request.user.is_superuser:
            raise PermissionDenied("Only the author of the course or the super-user can delete a page")

        kwargs['_obj'] = page #do this to avoid another database lookup in the super.obj_delete method
        return super(PageResource, self).delete_detail(request, **kwargs)

    def is_authorized(self, request, object=None):
        # because of a bug in tastypie, the object given to this method is always None. Thus authorization
        # is not possible. Therefore, we use other methods to deal with this problem.
        return True

    def apply_authorization_limits(self, request, object_list):
        authorized_objects = super(PageResource, self).apply_authorization_limits(request, object_list)
        if request.user.is_superuser:
            return authorized_objects
        elif request.method == 'GET':
            return authorized_objects.filter(Q(course__is_public=True) | Q(course__instructor__id=request.user.id))
        else:
            return authorized_objects.filter(course__instructor__id=request.user.id)

class CourseResource(ModelResource):
    instructor = fields.ForeignKey(UserResource, 'instructor', full=True)
    title = fields.CharField(attribute='title')
    pages = fields.OneToManyField(PageResource, 'pages', full=True)
    always_return_data = True
    
    class Meta:
        queryset = Course.objects.all()
        resource_name = 'courses'
        allowed_methods = ['get', 'patch']
        authentication = UberAuthentication()
        authorization = UberAuthorization()
        limit = 10
        ordering = ['title', 'popularity', 'instructor', 'creation_timestamp']
        filtering = {
            "instructor": ALL_WITH_RELATIONS,
        }
        serializer = UberSerializer()
        include_absolute_url = True
        excludes = []

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>{resource})/(?P<pk>\w[\w/-]*)/enroll{slash}'.format(
                resource=self._meta.resource_name,
                slash=trailing_slash()
            ), self.wrap_view('enroll'), name='api_course_enroll')
        ]

    def enroll(self, request, **kwargs):
        """
        This method will be used by the client to enroll the current user into the current course. Since this
        method changes the state of the system, only a POST or a PUT request will be responded to. In the future,
        it may be possible to return a boolean for a GET request indicating whether or not the current user is
        enrolled in the current course.
        """
        # if the request is not of the desired types, then deny
        if not request.method in ['POST', 'PUT', 'GET']:
            return BadRequest("Only a PUT, POST, or GET is allowed at this endpoint")

        # if the user is not authenticated then deny
        if not self._meta.authentication.is_authenticated(request):
            return HttpForbidden("Operation not authorized")

        try:
            course = self.cached_obj_get(request=request, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices("More than one resource is found at this URI")

        if request.method == 'GET':
            # the client just wants to find out whether or not the current user is enrolled with the current course
            if course.students.filter(username=request.user.username).count() == 1:
                #the student is enrolled
                return HttpResponse(True)
            else:
                return HttpResponse(False)
        elif request.method in ['POST', 'PUT']:
            # now that we have the course and the user, we should enroll the user in the course
            enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
            return HttpNoContent()

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

    def dehydrate(self, bundle):
        """
        1) Adds a page list uri to the courses object. This is because when a new page is created, a url is needed to
        send the post. Technically, this url could be constructed from the urls of the other pages, but that doesn't
        cover the scenario where there are no pages in the course. More importantly, it leaves some flexibility into
        the system.
        2) Adds the url of the thumbnail version of the photo.
        """
        from uberlearner.urls import v1_api
        if bundle.obj and bundle.data:
            bundle.data['page_list_uri'] = reverse('api_dispatch_list', kwargs={
                'resource_name': PageResource._meta.resource_name,
                'api_name': v1_api.api_name
            })
            if bundle.obj.photo:
                bundle.data['thumbnail'] = get_thumbnailer(bundle.obj.photo)['tile'].url
            bundle.data['creationTimePrecise'] = str(time.mktime(bundle.obj.creation_timestamp.timetuple())*1000)
        return bundle