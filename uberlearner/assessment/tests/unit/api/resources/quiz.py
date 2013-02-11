from django.core.urlresolvers import reverse
from django.test import Client
from tastypie.test import ResourceTestCase
from accounts.tests.factories import UserFactory
from assessment.api.resources.quiz import QuizResource
from assessment.models import Quiz
from assessment.tests.factories import QuizFactory
from courses.tests.factories import CourseFactory, EnrollmentFactory
from uberlearner.urls import v1_api


class QuizResourceValidationTests(ResourceTestCase):
    def setUp(self):
        super(QuizResourceValidationTests, self).setUp()
        #: :type: Course
        self.course = CourseFactory.create()
        self.quiz_list_uri = reverse('api_dispatch_list', kwargs={
            'resource_name': QuizResource._meta.resource_name,
            'api_name': v1_api.api_name
        })
        self.post_data = {
            'title': 'Test Title',
            'course': self.course.get_resource_uri()
        }

    def test_that_model_validation_carries_through(self):
        """
        All the tests regarding validation of the model have already been written for the quiz model. This test
        just tests whether the validation messages from the model class carry through during creation of quizzes
        using the api.
        """
        self.post_data['title'] = 'Really long title; ' * 100
        response = self.api_client.post(
            self.quiz_list_uri,
            format='json',
            data=self.post_data,
            authentication=self.create_basic(self.course.instructor.username, UserFactory._plain_text_password)
        )
        self.assertHttpBadRequest(response)
        content = self.deserialize(response)
        self.assertIn('quizzes', content)
        self.assertIn('title', content['quizzes'])


class QuizResourcePermissionTests(ResourceTestCase):
    def setUp(self):
        super(QuizResourcePermissionTests, self).setUp()
        #: :type: Course
        self.course = CourseFactory.create()
        self.random_user = UserFactory.create()
        self.enrolled_user = UserFactory.create()
        EnrollmentFactory.create(course=self.course, student=self.enrolled_user)
        self.course_resource_uri = self.course.get_resource_uri()
        self.quiz_list_uri = reverse('api_dispatch_list', kwargs={
            'resource_name': QuizResource._meta.resource_name,
            'api_name': v1_api.api_name
        })
        self.post_data = {
            'title': 'Test Title',
            'course': self.course.get_resource_uri()
        }

    def tearDown(self):
        self.course.enrollments.all().delete()
        self.course.delete()

    def _get_credentials(self, user):
        return self.create_basic(user.username, UserFactory._plain_text_password)

    def _perform_http_method_on_quiz(self, method=None, **kwargs):
        if method is None:
            raise ValueError('Some action has to be performed on the quiz endpoint')
        if not hasattr(self.api_client, method):
            raise ValueError('Illegal http method attempted on the quiz endpoint')

        if 'authentication' in kwargs and kwargs['authentication'] is not None:
            kwargs['authentication'] = self._get_credentials(kwargs['authentication'])

        pre_creation_count = Quiz.objects.count()
        response = getattr(self.api_client, method)(**kwargs)
        post_creation_count = Quiz.objects.count()

        return response, pre_creation_count, post_creation_count

    def _create_quiz(self, data=None, **kwargs):
        data = data or self.post_data
        return self._perform_http_method_on_quiz(method='post', uri=self.quiz_list_uri, data=data, **kwargs)

    def _read_quiz(self, quiz, **kwargs):
        if 'uri' in kwargs:
            del kwargs['uri']
        return self._perform_http_method_on_quiz(method='get', uri=quiz.get_resource_uri(), **kwargs)

    def _read_quiz_list(self, **kwargs):
        if 'uri' in kwargs:
            del kwargs['uri']
        return self._perform_http_method_on_quiz(method='get', uri=self.quiz_list_uri, **kwargs)

    def _update_quiz(self, quiz, data_update={}, **kwargs):
        if 'uri' in kwargs:
            del kwargs['uri']
        if 'data' in kwargs:
            del kwargs['data']
        return self._perform_http_method_on_quiz(method='put', uri=quiz.get_resource_uri(), data=data_update, **kwargs)

    def _delete_quiz(self, quiz, **kwargs):
        if 'uri' in kwargs:
            del kwargs['uri']
        return self._perform_http_method_on_quiz(method='delete', uri=quiz.get_resource_uri(), **kwargs)

    def test_that_authorized_users_can_create_quiz(self):
        response, pre_count, post_count = self._create_quiz(authentication=self.course.instructor)
        self.assertEqual(pre_count, post_count - 1)
        self.assertHttpCreated(response)

    def test_that_unauthorized_users_cannot_create_quiz(self):
        test_users = [None, self.random_user, self.enrolled_user]
        for test_user in test_users:
            response, pre_count, post_count = self._create_quiz(authentication=test_user)
            self.assertEqual(pre_count, post_count)
            self.assertHttpUnauthorized(response)

    def test_that_authorized_users_can_delete_quiz(self):
        quiz = QuizFactory.create(course=self.course)
        response, pre_count, post_count = self._delete_quiz(quiz=quiz, authentication=self.course.instructor)
        self.assertHttpAccepted(response)
        self.assertEqual(pre_count - 1, post_count)

    def test_that_unauthorized_users_cannot_delete_quiz(self):
        quiz = QuizFactory.create(course=self.course)
        test_users = [None, self.random_user, self.enrolled_user]
        for test_user in test_users:
            response, pre_count, post_count = self._delete_quiz(quiz=quiz, authentication=test_user)
            self.assertHttpUnauthorized(response)
            self.assertEqual(pre_count, post_count)

    def test_that_authorized_users_can_read_quiz(self):
        """
        Authorized users are: instructor, student
        """
        quiz = QuizFactory.create(course=self.course)
        test_users = [self.course.instructor, self.enrolled_user]
        for test_user in test_users:
            response, pre_count, post_count = self._read_quiz(quiz=quiz, authentication=test_user)
            self.assertValidJSONResponse(response)
            deserialized = self.deserialize(response)
            self.assertEqual(deserialized['id'], quiz.id)

    def test_that_unauthorized_users_cannot_read_quiz(self):
        quiz = QuizFactory.create(course=self.course)
        test_users = [None, self.random_user]
        for test_user in test_users:
            response, pre_count, post_count = self._read_quiz(quiz=quiz, authentication=test_user)
            self.assertHttpUnauthorized(response)

    def test_that_instructors_can_only_list_quizzes_from_their_courses(self):
        quiz_from_another_course = QuizFactory.create()
        quiz = QuizFactory.create(course=self.course)
        response, pre_count, post_count = self._read_quiz_list(authentication=quiz.course.instructor)
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['meta']['totalCount'], 1)
        self.assertEqual(len(deserialized['objects']), 1)
        self.assertEqual(deserialized['objects'][0]['id'], quiz.id)

    def test_that_students_can_only_list_quizzes_from_their_enrollments(self):
        # the enrollment factory creates its course and student as well
        enrollment = EnrollmentFactory.create()
        non_enrolled_quiz = QuizFactory.create(course=enrollment.course)
        enrolled_quiz = QuizFactory.create(course=self.course)
        response, pre_count, post_count = self._read_quiz_list(authentication=self.enrolled_user)
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['meta']['totalCount'], 1)
        self.assertEqual(len(deserialized['objects']), 1)
        self.assertEqual(deserialized['objects'][0]['id'], enrolled_quiz.id)

    def test_that_unauthorized_users_cannot_list_quizzes(self):
        quiz = QuizFactory.create(course=self.course)
        response, pre_count, post_count = self._read_quiz_list(authentication=None)
        self.assertHttpUnauthorized(response)

    def test_that_authorized_users_can_update_quiz(self):
        quiz = QuizFactory.create(course=self.course)
        response, pre_count, post_count = self._update_quiz(
            quiz,
            data_update={'title': 'New and improved'},
            authentication=self.course.instructor
        )
        self.assertHttpAccepted(response)
        quiz = Quiz.objects.get(pk=quiz.pk)
        self.assertEqual(quiz.title, 'New and improved')

    def test_that_unauthorized_users_cannot_update_quiz(self):
        quiz = QuizFactory.create(course=self.course)
        original_title = quiz.title
        response, pre_count, post_count = self._update_quiz(
            quiz,
            data_update={'title': 'New and improved'}
        )
        self.assertHttpUnauthorized(response)
        self.assertEqual(original_title, quiz.title)

        response, pre_count, post_count = self._update_quiz(
            quiz,
            data_update={'title': 'New and improved'},
            authentication=self.enrolled_user
        )
        self.assertHttpUnauthorized(response)
        self.assertEqual(original_title, quiz.title)

        response, pre_count, post_count = self._update_quiz(
            quiz,
            data_update={'title': 'New and improved'},
            authentication=self.random_user
        )
        self.assertHttpUnauthorized(response)
        self.assertEqual(original_title, quiz.title)


class QuizResourceMethodTests(ResourceTestCase):
    pass