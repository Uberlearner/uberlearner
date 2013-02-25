from django.core.urlresolvers import reverse
from tastypie.test import ResourceTestCase
from accounts.tests.factories import UserFactory
from assessment.api.resources.quiz import QuizResource
from assessment.models import Quiz
from assessment.tests.factories import QuizFactory, QuestionSetFactory
from courses.tests.factories import CourseFactory, EnrollmentFactory
from main.tests.api import UberResourceTestCase
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


class QuizResourcePermissionTests(UberResourceTestCase):
    class Meta(UberResourceTestCase.Meta):
        model = Quiz
        list_uri = reverse('api_dispatch_list', kwargs={
            'resource_name': QuizResource._meta.resource_name,
            'api_name': v1_api.api_name
        })

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

    def test_that_authorized_users_can_create_quiz(self):
        response, pre_count, post_count = self._create(data=self.post_data, authentication=self.course.instructor)
        self.assertEqual(pre_count, post_count - 1)
        self.assertHttpCreated(response)

    def test_that_authorized_users_can_read_quiz(self):
        """
        Authorized users are: instructor, student. Test any one.
        """
        quiz = QuizFactory.create(course=self.course)
        test_users = [self.enrolled_user]
        for test_user in test_users:
            response, pre_count, post_count = self._read(obj=quiz, authentication=test_user)
            self.assertValidJSONResponse(response)
            deserialized = self.deserialize(response)
            self.assertEqual(deserialized['id'], quiz.id)

    def test_that_authorized_users_can_update_quiz(self):
        quiz = QuizFactory.create(course=self.course)
        response, pre_count, post_count = self._update(
            quiz,
            data_update={'title': 'New and improved'},
            authentication=self.course.instructor
        )
        self.assertHttpAccepted(response)
        quiz = Quiz.objects.get(pk=quiz.pk)
        self.assertEqual(quiz.title, 'New and improved')

    def test_that_authorized_users_can_delete_quiz(self):
        quiz = QuizFactory.create(course=self.course)
        response, pre_count, post_count = self._delete(obj=quiz, authentication=self.course.instructor)
        self.assertHttpAccepted(response)
        self.assertEqual(pre_count - 1, post_count)

    def test_that_unauthorized_users_cannot_create_quiz(self):
        response, pre_count, post_count = self._create(data=self.post_data, authentication=self.random_user)
        self.assertEqual(pre_count, post_count)
        self.assertHttpUnauthorized(response)

    def test_that_unauthorized_users_cannot_read_quiz(self):
        quiz = QuizFactory.create(course=self.course)
        response, pre_count, post_count = self._read(obj=quiz, authentication=None)
        self.assertHttpUnauthorized(response)

    def test_that_unauthorized_users_cannot_update_quiz(self):
        quiz = QuizFactory.create(course=self.course)
        original_title = quiz.title
        response, pre_count, post_count = self._update(
            quiz,
            data_update={'title': 'New and improved'}
        )
        self.assertHttpUnauthorized(response)
        self.assertEqual(original_title, quiz.title)

    def test_that_unauthorized_users_cannot_delete_quiz(self):
        quiz = QuizFactory.create(course=self.course)
        response, pre_count, post_count = self._delete(obj=quiz, authentication=self.random_user)
        self.assertHttpUnauthorized(response)
        self.assertEqual(pre_count, post_count)

    def test_that_instructors_can_only_list_quizzes_from_their_courses(self):
        quiz_from_another_course = QuizFactory.create()
        quiz = QuizFactory.create(course=self.course)
        response, pre_count, post_count = self._read_list(authentication=quiz.course.instructor)
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
        response, pre_count, post_count = self._read_list(authentication=self.enrolled_user)
        self.assertValidJSONResponse(response)
        deserialized = self.deserialize(response)
        self.assertEqual(deserialized['meta']['totalCount'], 1)
        self.assertEqual(len(deserialized['objects']), 1)
        self.assertEqual(deserialized['objects'][0]['id'], enrolled_quiz.id)

    def test_that_unauthorized_users_cannot_list_quizzes(self):
        quiz = QuizFactory.create(course=self.course)
        response, pre_count, post_count = self._read_list(authentication=None)
        self.assertHttpUnauthorized(response)

    def test_that_students_cannot_see_question_sets(self):
        white_list = ['id', 'title', 'summary', 'course', 'gradingMethod', 'attemptsAllowed', 'reattemptInterval',
                      'questionCount', 'points', 'resourceUri', 'lastModified', 'creationTimestamp']
        black_list = ['questionSets']
        question_set = QuestionSetFactory.create(quiz__course=self.course)
        response, pre_count, post_count = self._read(obj=question_set.quiz, authentication=self.enrolled_user)
        self.assertValidJSONResponse(response)
        quiz = self.deserialize(response)
        self._test_packet_attributes(quiz, white_list, black_list)

    def test_that_instructors_can_see_all_attributes_of_question_sets(self):
        white_list = ['id', 'title', 'summary', 'course', 'gradingMethod', 'attemptsAllowed', 'reattemptInterval',
                      'questionCount', 'points', 'questionSets', 'resourceUri', 'lastModified', 'creationTimestamp']
        black_list = []
        question_set = QuestionSetFactory.create(quiz__course=self.course)
        response, pre_count, post_count = self._read(obj=question_set.quiz, authentication=self.course.instructor)
        self.assertValidJSONResponse(response)
        quiz = self.deserialize(response)
        self._test_packet_attributes(quiz, white_list, black_list)