from django.core.exceptions import ValidationError
from django.test import TestCase
from accounts.tests.factories import UserFactory
from assessment.exceptions import EmptyQuizAttemptedException
from assessment.tests.factories import QuizFactory, QuestionSetFactory, BooleanQuestionFactory


class QuizValidationTests(TestCase):
    def test_that_summary_cannot_be_too_long(self):
        quiz = QuizFactory.create(summary='test summary'*100)
        self.assertRaises(ValidationError, quiz.full_clean)

    def test_that_title_cannot_be_too_long(self):
        quiz = QuizFactory.create(title='test title '*100)
        self.assertRaises(ValidationError, quiz.full_clean)

    def test_that_attempts_allowed_cannot_be_zero(self):
        quiz = QuizFactory.create(attempts_allowed=0)
        self.assertRaises(ValidationError, quiz.full_clean)


class QuizPropertyTests(TestCase):
    def setUp(self):
        self.quiz = QuizFactory.create()

    def tearDown(self):
        self.quiz.delete()

    def test_empty_quiz_points(self):
        self.assertEqual(self.quiz.points, 0)


class QuizMethodTests(TestCase):
    def setUp(self):
        self.quiz = QuizFactory.create()

    def tearDown(self):
        self.quiz.delete()

    def test_question_set_creation(self):
        question_set = self.quiz.generate_question_set(points_per_question=2)
        self.assertIsNotNone(question_set)
        self.assertEquals(question_set.quiz, self.quiz)
        question_set = self.quiz.generate_question_set(create=False, points_per_question=2)
        self.assertIsNotNone(question_set)
        self.assertEquals(question_set.quiz, self.quiz)

    def test_that_empty_quiz_cannot_be_attempted(self):
        user = UserFactory.create()
        self.assertRaises(EmptyQuizAttemptedException, self.quiz.generate_attempt, user)

    def test_attempt_creation(self):
        """
        Tests whether a quiz attempt can be properly generated
        """
        # A boolean-question-factory will also create the corresponding question-set and quiz
        #: :type: BooleanQuestion
        boolean_question = BooleanQuestionFactory.create()
        quiz = boolean_question.question_set.quiz
        user = UserFactory.create()
        attempt = quiz.generate_attempt(user)
        self.assertIsNotNone(attempt)