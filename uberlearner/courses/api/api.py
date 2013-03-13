import json
from django.conf.urls import url
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from easy_thumbnails.files import get_thumbnailer
from tastypie.authentication import Authentication
from tastypie.exceptions import ImmediateHttpResponse, BadRequest
from tastypie.http import HttpGone, HttpMultipleChoices, HttpNoContent, HttpForbidden
from tastypie.resources import ModelResource, convert_post_to_patch
from tastypie import fields, http
from tastypie.utils import trailing_slash
import types
from accounts.api.api import UserResource
from accounts.models import UserProfile
from main.api.authentication import UberAuthentication
from courses.api.authorization import CourseAuthorization
from main.api.serializers import UberSerializer
from courses.models import Course, Instructor, Page, Enrollment
from django.contrib.auth.models import User              
from tastypie.constants import ALL_WITH_RELATIONS
from django.core.urlresolvers import reverse
import time
from django.conf import settings

MAX_COURSE_SCORE = settings.COURSE_RATING_RANGE

class PageResource(ModelResource):
    class Meta:
        queryset = Page.objects.all()
        authentication = UberAuthentication()
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

    def hydrate_estimated_effort(self, bundle):
        if 'estimated_effort' in bundle.data:
            effort = bundle.data['estimated_effort']
            if isinstance(effort, basestring):
                effort = effort.strip()
                if effort:
                    bundle.data['estimated_effort'] = int(effort)
                else:
                    bundle.data['estimated_effort'] = None
        return bundle

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
        authorization = CourseAuthorization()
        limit = 10
        ordering = ['title', 'popularity', 'instructor', 'creation_timestamp']
        filtering = {
            "instructor": ALL_WITH_RELATIONS,
        }
        serializer = UberSerializer()
        include_absolute_url = True
        excludes = ['rating_score']

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>{resource})/(?P<pk>\w[\w/-]*)/enroll{slash}'.format(
                resource=self._meta.resource_name,
                slash=trailing_slash()
            ), self.wrap_view('enroll'), name='api_course_enroll'),
            url(r'^(?P<resource_name>{resource})/(?P<pk>\w[\w/-]*)/rate{slash}'.format(
                resource=self._meta.resource_name,
                slash=trailing_slash()
            ), self.wrap_view('rate'), name='api_course_rate'),
        ]

    def _format_rating(self, rating):
        return "{:.1f}".format(rating)

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

    def rate(self, request, **kwargs):
        """
        This method is used by the client to let the user rate a particular course.
        Only post requests will be allowed. The response will contain a set of parameters
        indicating the new ratings of the course (weighted, unweighted and user).
        """
        # if the request is not of the desired types, then deny
        if request.method != 'POST':
            return BadRequest("Only a POST is allowed at this endpoint")

        # if the user is not authenticated then deny
        if not self._meta.authentication.is_authenticated(request):
            return HttpForbidden("Operation not authorized")

        try:
            course = self.cached_obj_get(request=request, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices("More than one resource is found at this URI")

        #In order for a user to rate a course, the user must be enrolled in that course
        if not course.is_enrolled(request.user):
            return HttpForbidden("You have to be enrolled in a course to rate it")

        score = int(request.POST['score'])
        if not (score >= 1 and score <= MAX_COURSE_SCORE):
            return HttpForbidden('Scores for courses have to be between 1 and 5 (inclusive)')

        response = course.rating.add(score=score, user=request.user, ip_address=request.META['REMOTE_ADDR'], commit=True)

        if 'status_code' not in response or response.status_code == 200:
            return HttpResponse(self._meta.serializer.to_json({
                'overall_weighted_rating': course.rating.get_rating(),
                'overall_unweighted_rating': self._format_rating(course.rating.get_real_rating()),
            }))
        else:
            return response

    def apply_filters(self, request, applicable_filters):
        # if the filters list has instructor, then modify its value to be the actual user
        if 'instructor__exact' in applicable_filters:
            instructor_username = applicable_filters['instructor__exact']
            if isinstance(instructor_username, basestring):
                applicable_filters['instructor__exact'] = User.objects.get(username=instructor_username)

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

    def is_valid(self, bundle, request=None):
        if request and hasattr(request, 'method') and request.method in ['POST', 'PATCH', 'PUT']:
            if not bundle.data['is_public'] and bundle.obj.enrollments.all().exists():
                if not bundle.obj.is_public:
                    # interestingly, this course has enrollments even though it is private. This should never happen and
                    # is an invalid state
                    raise ValueError('Course {course} is somehow un-published even though it has enrollments'.format(
                        course=bundle.obj
                    ))
                else:
                    #someone is attempting to make this course private even though it has enrollments
                    return False
        return True

    def dehydrate_pages(self, bundle):
        if 'pages' in bundle.data and isinstance(bundle.data['pages'], list):
            for page in bundle.data['pages']:
                if 'html' in page.data:
                    page.data.pop('html')
            return bundle.data['pages']

    def hydrate_photo(self, bundle):
        if 'photo' in bundle.data:
            #either the photo url is absolute or not. This can be determined by using a split on .com
            url_split = bundle.data['photo'].split('.com')
            if len(url_split) == 2:
                #This must mean that ".com" existed in the url and hence the url was absolute
                bundle.data['photo'] = url_split[1].replace('/courses/', '')
        return bundle

    def dehydrate(self, bundle):
        """
        1) Adds a page list uri to the courses object. This is because when a new page is created, a url is needed to
        send the post. Technically, this url could be constructed from the urls of the other pages, but that doesn't
        cover the scenario where there are no pages in the course. More importantly, it leaves some flexibility into
        the system.
        2) Adds the url of the thumbnail version of the photo.
        3) Adds the overall rating of the course.
        4) Adds the user's rating for the course if the user is not anonymous.
        5) Adds the url at which ratings can be posted.
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

            if bundle.request.user.is_anonymous():
                bundle.data['enrolled'] = None
            elif bundle.obj.enrollments.filter(student=bundle.request.user).exists():
                bundle.data['enrolled'] = True
            else:
                bundle.data['enrolled'] = False

            bundle.data['overall_unweighted_rating'] = self._format_rating(bundle.obj.rating.get_real_rating())
            bundle.data['overall_weighted_rating'] = bundle.obj.rating.get_rating()

            if not bundle.request.user.is_anonymous():
                bundle.data['user_rating'] = bundle.obj.rating.get_rating_for_user(bundle.request.user)

            bundle.data['rating_resource_uri'] = bundle.obj.get_rating_resource_uri()
        return bundle

class EnrollmentResource(ModelResource):
    course = fields.ForeignKey(CourseResource, 'course', full=True)
    student = fields.ForeignKey(UserResource, 'student', full=True)
    class Meta:
        queryset = Enrollment.objects.all()
        authentication = UberAuthentication()
        authorization = CourseAuthorization()
        serializer = UberSerializer()
        resource_name = 'enrollments'
        filtering = {
            'course': ALL_WITH_RELATIONS,
            'student': ALL_WITH_RELATIONS
        }
        ordering = ['course']

    def apply_filters(self, request, applicable_filters):
        # if the filters list has instructor, then modify its value to be the actual user
        if 'student__exact' in applicable_filters:
            student_username = applicable_filters['student__exact']
            if isinstance(student_username, basestring):
                applicable_filters['student__exact'] = User.objects.get(username=student_username)

        result = super(EnrollmentResource, self).apply_filters(request, applicable_filters)
        return result
