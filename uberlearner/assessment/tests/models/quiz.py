from django.core.exceptions import ValidationError
from django.test import TestCase
from accounts.tests.factories import UserFactory
from assessment.exceptions import EmptyQuizAttemptedException
from courses.tests.factories import CourseFactory
from assessment.tests.factories import QuizFactory, QuestionSetFactory, QuestionFactory, BooleanQuestionFactory

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

class QuestionSetValidationTests(TestCase):
    def test_that_points_are_not_zero(self):
        question_set = QuestionSetFactory.create(points_per_question=0)
        self.assertRaises(ValidationError, question_set.full_clean)

    def test_that_points_are_not_negative(self):
        question_set = QuestionSetFactory.create(points_per_question=-1)
        self.assertRaises(ValidationError, question_set.full_clean)

    def test_that_fault_penalty_is_not_negative(self):
        question_set = QuestionSetFactory.create(fault_penalty=-1)
        self.assertRaises(ValidationError, question_set.full_clean)

    def test_that_title_cannot_be_too_long(self):
        title = 'sample title ' * 100
        question_set = QuestionSetFactory.create(title=title)
        self.assertRaises(ValidationError, question_set.full_clean)

    def test_that_summary_cannot_be_too_long(self):
        summary = 'sample summary ' * 200
        question_set = QuestionSetFactory.create(summary=summary)
        self.assertRaises(ValidationError, question_set.full_clean)

    def test_that_displayed_question_count_cannot_be_negative(self):
        question_set = QuestionSetFactory.create(displayed_question_count=-1)
        self.assertRaises(ValidationError, question_set.full_clean)

    def test_that_displayed_question_count_cannot_be_zero(self):
        question_set = QuestionSetFactory.create(displayed_question_count=0)
        self.assertRaises(ValidationError, question_set.full_clean)

    def test_that_fault_penalty_cannot_be_greater_than_points_per_question(self):
        question_set = QuestionSetFactory.create(fault_penalty=3, points_per_question=2)
        self.assertRaises(ValidationError, question_set.full_clean)

class QuestionSetPropertyTests(TestCase):
    def test_empty_question_set_points(self):
        question_set = QuestionSetFactory.create()
        self.assertEqual(question_set.points, 0)

    def test_question_starved_question_set_points(self):
        question_set = QuestionSetFactory.create(points_per_question=2, displayed_question_count=3)
        questions = BooleanQuestionFactory.create(question_set=question_set)
        self.assertEqual(question_set.points, 2)

    def test_full_question_set_points(self):
        question_set = QuestionSetFactory.create(points_per_question=2, displayed_question_count=3)
        questions = BooleanQuestionFactory.create_batch(3, question_set=question_set)
        self.assertEqual(question_set.points, 6)

    def test_over_filled_question_set_points(self):
        question_set = QuestionSetFactory.create(points_per_question=2, displayed_question_count=3)
        questions = BooleanQuestionFactory.create_batch(5, question_set=question_set)
        self.assertEqual(question_set.points, 6)

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

class QuizPropertyTests(TestCase):
    def setUp(self):
        self.quiz = QuizFactory.create()

    def tearDown(self):
        self.quiz.delete()

    def test_empty_quiz_points(self):
        self.assertEqual(self.quiz.points, 0)

class QuizAttemptTests(TestCase):
    def test_that_empty_quiz_cannot_be_attempted(self):
        quiz = QuizFactory.create()
        user = UserFactory.create()
        self.assertRaises(EmptyQuizAttemptedException, quiz.generate_attempt, user)