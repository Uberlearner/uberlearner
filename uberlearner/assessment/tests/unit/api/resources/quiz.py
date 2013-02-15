from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
import fudge
from accounts.tests.factories import UserFactory
from assessment.tests.factories import QuizFactory
from assessment.api.resources.quiz import QuizResource
from assessment.models import Quiz
from courses.tests.factories import EnrollmentFactory


class TestQuizAuthorizationLimits(TestCase):
    def setUp(self):
        self.resource = QuizResource()
        self.object_list = Quiz.objects.all()
        self.quiz = QuizFactory.create()
        self.course = self.quiz.course

    def tearDown(self):
        self.quiz.course.instructor.delete()  # cascades to the other objects

    def _generate_request(self, user):
        request = fudge.Fake('request').has_attr(user=user)
        return request

    def test_that_anonymous_users_cannot_access_anything(self):
        request = self._generate_request(AnonymousUser())
        quizzes = self.resource.apply_authorization_limits(request, self.object_list)
        self.assertEqual(quizzes.count(), 0)

    def test_that_random_authorized_users_cannot_access_quizzes(self):
        random_user = UserFactory.create()
        request = self._generate_request(random_user)
        quizzes = self.resource.apply_authorization_limits(request, self.object_list)
        self.assertEqual(quizzes.count(), 0)

    def test_that_enrolled_users_can_only_access_their_quizzes(self):
        enrollment = EnrollmentFactory.create(course=self.course)
        enrolled_user = enrollment.student
        non_enrolled_quiz = QuizFactory.create()  # this should have a different course
        self.assertNotEqual(self.course, non_enrolled_quiz.course)

        request = self._generate_request(enrolled_user)
        quizzes = self.resource.apply_authorization_limits(request, self.object_list)
        self.assertEqual(quizzes.count(), 1)
        quiz = quizzes[0]
        self.assertEqual(quiz.course, self.course)

    def test_that_instructors_can_access_all_their_quizzes(self):
        random_quiz = QuizFactory.create()
        random_course = random_quiz.course
        self.assertNotEqual(random_course, self.course)

        request = self._generate_request(self.course.instructor)
        quizzes = self.resource.apply_authorization_limits(request, self.object_list)
        self.assertEqual(quizzes.count(), 1)
        quiz = quizzes[0]
        self.assertEqual(quiz.course, self.course)