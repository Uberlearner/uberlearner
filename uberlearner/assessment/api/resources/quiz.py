import collections
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation
from django.db.models import Q, F
from django.db.models.query import QuerySet
from tastypie import fields
from tastypie.authentication import BasicAuthentication
from assessment.models import Quiz
from courses.api import CourseResource
from courses.models import Course
from main.api import UberModelResource
from main.api.authorization import UberAuthorization
from main.api.validation import UberModelValidation


class QuizResourceAuthorization(UberAuthorization):
    def is_get_method_authorized(self, obj, user):
        # this could be a GET for the quiz list or an individual quiz
        if obj is not None:  # this must refer to a particular quiz
            if user.is_anonymous():
                return False
            elif user == obj.course.instructor:
                return True
            elif obj.course.enrollments.filter(student=user).exists():
                return True
            else:
                return False
        else:  # this must be a request for a list of quizzes
            if user.is_anonymous():
                return False
            else:
                return True

    def is_post_method_authorized(self, obj, user, data):
        if user.is_anonymous():
            return False

        course = None
        if obj is not None:
            course = obj.course
        elif 'course' in data:
            course = self.get_object(data['course'], object_class=Course)
        else:
            raise ObjectDoesNotExist('Could not get the required course')

        return course.instructor == user

    def are_put_and_patch_methods_authorized(self, obj, user, data):
        if user.is_anonymous() or obj is None:
            return False

        course = obj.course
        if 'course' in data and data['course'] != course:
            raise SuspiciousOperation('The quiz does not belong to the course mentioned in the request data')

        return user.pk == course.instructor.pk

    def is_delete_method_authorized(self, obj, user):
        if user.is_anonymous() or obj is None:
            return False

        return user.pk == obj.course.pk

    def _get_request_data(self, request):
        if request.method == 'POST':
            data = request.raw_post_data
            data = self.resource_meta.serializer.deserialize(data)
            return data
        else:
            return {}

    def is_authorized(self, request, obj=None):
        if obj is None:
            obj = self.get_object(request.path)  # it is possible for the object to still be None

        request_data = self._get_request_data(request)

        if request.method == 'GET':
            return self.is_get_method_authorized(obj, request.user)
        elif request.method == 'POST':
            return self.is_post_method_authorized(obj, request.user, request_data)
        elif request.method == 'PUT' or request.method == 'PATCH':
            return self.are_put_and_patch_methods_authorized(obj, request.user, request_data)
        elif request.method == 'DELETE':
            return self.is_delete_method_authorized(obj, request.user)
        else:
            raise Exception('Unauthorized method ({0}) attempted'.format(request.method))

    def apply_limits(self, request, object_list):
        if request.user.is_anonymous():
            return QuerySet.none()
        else:
            # first generate Q filter to check whether the quiz belongs to one of the user's enrollments
            enrollment_q_filter = None
            for enrollment in request.user.enrollments.all():
                enrollment_q_filter = enrollment_q_filter or Q(course=enrollment.course)
            # filter the object_list by adding in a q_filter to check if the user is the course's instructor
            return object_list.filter(
                enrollment_q_filter or
                Q(course__instructor__username=request.user.username)
            )


class QuizResource(UberModelResource):
    course = fields.ForeignKey(CourseResource, 'course')

    class Meta(UberModelResource.Meta):
        resource_name = 'quizzes'
        queryset = Quiz.objects.all()
        authorization = QuizResourceAuthorization()
        allowed_methods = ['get', 'post', 'patch', 'put', 'delete']
        validation = UberModelValidation()