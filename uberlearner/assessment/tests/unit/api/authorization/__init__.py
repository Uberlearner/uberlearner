from django.contrib.auth.models import User, AnonymousUser
from django.core.urlresolvers import reverse
from django.test import TestCase
from assessment.api.authorization import QuizRelatedResourceAuthorization
from assessment.api.resources.quiz import QuizResource
from assessment.models import Quiz
from assessment.tests.factories import QuizFactory
from courses.tests.factories import EnrollmentFactory
from main.api import UberSerializer
from uberlearner.urls import v1_api
import json

from .quiz import *


def merge_dicts(first, second):
    return dict(first.items() + second.items())


def generate_authorization(course, object_class=Quiz):
    """
    Creates an instance of the QuizRelatedResourceAuthorization class by using a get_course
    method that merely returns the course variable given to this method.
    """
    class AuthorizationClass(QuizRelatedResourceAuthorization):
        def __init__(self):
            Meta = type('Meta', (object, ), {
                'object_class': object_class,
                'serializer': UberSerializer()
            })
            self.resource_meta = Meta()

        def get_course(self, obj=None, data=None):
            return course

    return AuthorizationClass()


def generate_request(path=None, method='GET', user=None, data={}):
    attributes = {
        'path': path or '/does/not/matter',
        'method': method or 'GET',
        'user': user or AnonymousUser(),
        'raw_post_data': None
    }

    klass = type('request', (object, ), attributes)
    request = klass()

    if method and method in ['POST']:
        request.raw_post_data = json.dumps(data)

    return request

QUIZ_LIST_URL = reverse('api_dispatch_list', kwargs={
    'resource_name': QuizResource._meta.resource_name,
    'api_name': v1_api.api_name
})

BASE_QUIZ_DATA = {
    'title': 'Test Quiz'
}


class AnonymousUsersTest(TestCase):
    def setUp(self):
        self.authorization = generate_authorization(None)

    def test_that_anonymous_users_cannot_get(self):
        request = generate_request(method='GET')
        is_authorized = self.authorization.is_authorized(request)
        self.assertFalse(is_authorized)

    def test_that_anonymous_users_cannot_post(self):
        request = generate_request(method='POST')
        is_authorized = self.authorization.is_authorized(request)
        self.assertFalse(is_authorized)

    def test_that_anonymous_users_cannot_put(self):
        request = generate_request(method='PUT')
        is_authorized = self.authorization.is_authorized(request)
        self.assertFalse(is_authorized)

    def test_that_anonymous_users_cannot_patch(self):
        request = generate_request(method='PATCH')
        is_authorized = self.authorization.is_authorized(request)
        self.assertFalse(is_authorized)

    def test_that_anonymous_users_cannot_delete(self):
        request = generate_request(method='DELETE')
        is_authorized = self.authorization.is_authorized(request)
        self.assertFalse(is_authorized)


class InstructorTest(TestCase):
    def setUp(self):
        self.own_quiz = QuizFactory.create()
        self.own_course = self.own_quiz.course
        self.instructor = self.own_course.instructor
        self.other_quiz = QuizFactory.create()
        self.other_course = self.other_quiz.course

    def tearDown(self):
        self.instructor.delete()
        self.other_course.instructor.delete()

    def test_that_quiz_for_own_course_can_be_created(self):
        authorization = generate_authorization(self.own_course)
        request = generate_request(method='POST', path=QUIZ_LIST_URL, data=merge_dicts(BASE_QUIZ_DATA, {
            'course': self.own_course.get_resource_uri()
        }), user=self.instructor)
        is_authorized = authorization.is_authorized(request)
        self.assertTrue(is_authorized)

    def test_that_quiz_for_other_course_cannot_be_created(self):
        authorization = generate_authorization(self.other_course)
        request = generate_request(method='POST', path=QUIZ_LIST_URL, data=merge_dicts(BASE_QUIZ_DATA, {
            'course': self.own_course.get_resource_uri()
        }), user=self.instructor)
        is_authorized = authorization.is_authorized(request)
        self.assertFalse(is_authorized)

    def test_that_quiz_for_own_course_can_be_modified(self):
        authorization = generate_authorization(self.own_course)
        request = generate_request(method='PUT', path=self.own_quiz.get_resource_uri(), user=self.instructor, data={
            'title': 'new title'
        })
        is_authorized = authorization.is_authorized(request)
        self.assertTrue(is_authorized)

    def test_that_quiz_for_other_course_cannot_be_modified(self):
        authorization = generate_authorization(self.other_course)
        request = generate_request(method='PUT', path=self.other_quiz.get_resource_uri(), user=self.instructor, data={
            'title': 'new title'
        })
        is_authorized = authorization.is_authorized(request)
        self.assertFalse(is_authorized)

    def test_that_quiz_for_own_course_can_be_read(self):
        authorization = generate_authorization(self.own_course)
        request = generate_request(method='GET', path=self.own_quiz.get_resource_uri(), user=self.instructor)
        is_authorized = authorization.is_authorized(request)
        self.assertTrue(is_authorized)

    def test_that_quiz_for_other_course_cannot_be_read(self):
        authorization = generate_authorization(self.other_course)
        request = generate_request(method='GET', path=self.other_quiz.get_resource_uri(), user=self.instructor)
        is_authorized = authorization.is_authorized(request)
        self.assertFalse(is_authorized)

    def test_that_quiz_for_own_course_can_be_deleted(self):
        authorization = generate_authorization(self.own_course)
        request = generate_request(method='DELETE', path=self.own_quiz.get_resource_uri(), user=self.instructor)
        is_authorized = authorization.is_authorized(request)
        self.assertTrue(is_authorized)

    def test_that_quiz_for_other_course_cannot_be_deleted(self):
        authorization = generate_authorization(self.other_course)
        request = generate_request(method='DELETE', path=self.other_quiz.get_resource_uri(), user=self.instructor)
        is_authorized = authorization.is_authorized(request)
        self.assertFalse(is_authorized)


class NonInstructorTest(TestCase):
    def setUp(self):
        self.enrollment = EnrollmentFactory.create()
        self.user = self.enrollment.student
        self.own_course = self.enrollment.course
        self.own_quiz = QuizFactory.create(course=self.own_course)

        self.another_enrollment = EnrollmentFactory.create()
        self.another_user = self.another_enrollment.student
        self.another_course = self.another_enrollment.course
        self.another_quiz = QuizFactory.create(course=self.another_course)

        self.non_instructors = [self.user, self.another_user]

    def tearDown(self):
        self.own_course.instructor.delete()
        self.user.delete()
        self.another_course.instructor.delete()
        self.another_user.delete()

    def test_that_objects_cannot_be_created_by_non_instructors(self):
        authorization = generate_authorization(self.own_course)
        for non_instructor in self.non_instructors:
            request = generate_request(path=QUIZ_LIST_URL, method='POST', data=merge_dicts(BASE_QUIZ_DATA, {
                'course': self.own_course.get_resource_uri()
            }), user=non_instructor)
            is_authorized = authorization.is_authorized(request)
            self.assertFalse(is_authorized)

    def test_that_objects_cannot_be_deleted_by_non_instructors(self):
        authorization = generate_authorization(self.own_course)
        for non_instructor in self.non_instructors:
            request = generate_request(path=self.own_quiz.get_resource_uri(), method='DELETE', user=non_instructor)
            is_authorized = authorization.is_authorized(request)
            self.assertFalse(is_authorized)

    def test_that_objects_cannot_be_updated_by_non_instructors(self):
        authorization = generate_authorization(self.own_course)
        for non_instructor in self.non_instructors:
            request = generate_request(path=self.own_quiz.get_resource_uri(), method='PUT', data={
                'title': 'new title'
            }, user=non_instructor)
            is_authorized = authorization.is_authorized(request)
            self.assertFalse(is_authorized)

    def test_that_enrolled_quiz_cannot_be_read_by_non_enrolled_user(self):
        authorization = generate_authorization(self.another_course)
        request = generate_request(path=self.another_quiz.get_resource_uri(), user=self.user)
        is_authorized = authorization.is_authorized(request)
        self.assertFalse(is_authorized)

    def test_that_enrolled_quiz_can_be_read_by_enrolled_user(self):
        authorization = generate_authorization(self.another_course)
        request = generate_request(path=self.another_quiz.get_resource_uri(), user=self.another_user)
        is_authorized = authorization.is_authorized(request)
        self.assertTrue(is_authorized)