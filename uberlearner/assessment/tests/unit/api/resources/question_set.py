from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
import fudge
from accounts.tests.factories import UserFactory
from assessment.tests.factories import QuestionSetFactory, QuizFactory
from assessment.api.resources.question_set import QuestionSetResource
from assessment.models import QuestionSet
from courses.tests.factories import EnrollmentFactory


class TestQuestionSetAuthorizationLimits(TestCase):
    def setUp(self):
        self.resource = QuestionSetResource()
        self.object_list = QuestionSet.objects.all()
        self.question_set = QuestionSetFactory.create()
        self.course = self.question_set.quiz.course

    def tearDown(self):
        self.question_set.quiz.course.instructor.delete()  # cascades to the other objects

    def _generate_request(self, user):
        request = fudge.Fake('request').has_attr(user=user)
        return request

    def test_that_anonymous_users_cannot_access_anything(self):
        request = self._generate_request(AnonymousUser())
        question_sets = self.resource.apply_authorization_limits(request, self.object_list)
        self.assertEqual(question_sets.count(), 0)

    def test_that_random_authorized_users_cannot_access_question_sets(self):
        random_user = UserFactory.create()
        request = self._generate_request(random_user)
        question_sets = self.resource.apply_authorization_limits(request, self.object_list)
        self.assertEqual(question_sets.count(), 0)

    def test_that_enrolled_users_can_only_access_their_question_sets(self):
        enrollment = EnrollmentFactory.create(course=self.course)
        enrolled_user = enrollment.student
        non_enrolled_question_set = QuestionSetFactory.create()  # this should have a different course
        self.assertNotEqual(self.course, non_enrolled_question_set.quiz.course)

        request = self._generate_request(enrolled_user)
        question_sets = self.resource.apply_authorization_limits(request, self.object_list)
        self.assertEqual(question_sets.count(), 1)
        question_set = question_sets[0]
        self.assertEqual(question_set.quiz.course, self.course)

    def test_that_instructors_can_access_all_their_quizzes(self):
        random_question_set = QuestionSetFactory.create()
        random_course = random_question_set.quiz.course
        self.assertNotEqual(random_course, self.course)

        request = self._generate_request(self.course.instructor)
        question_sets = self.resource.apply_authorization_limits(request, self.object_list)
        self.assertEqual(question_sets.count(), 1)
        question_set = question_sets[0]
        self.assertEqual(question_set.quiz.course, self.course)
