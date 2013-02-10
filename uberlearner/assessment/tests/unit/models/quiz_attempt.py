from django.test import TestCase

# A QuizAttempt is a very simple model. Validation tests for this is not yet necessary.
from assessment.tests.factories import QuizAttemptFactory, BooleanQuestionAttemptFactory, \
    MultipleChoiceQuestionAttemptFactory, QuizFactory, QuestionSetFactory


class QuizAttemptPropertyTests(TestCase):
    def test_empty_quiz_attempt_all_question_attempts(self):
        quiz_attempt = QuizAttemptFactory.create()
        self.assertEqual(quiz_attempt.all_question_attempts, [])

    def test_boolean_attempts_only_all_question_attempts(self):
        quiz_attempt = QuizAttemptFactory.create(boolean_attempt_count=2)
        self.assertEqual(len(quiz_attempt.all_question_attempts), 2)

    def test_multiple_choice_attempts_only_all_question_attempts(self):
        quiz_attempt = QuizAttemptFactory.create(multiple_choice_attempt_count=3)
        self.assertEqual(len(quiz_attempt.all_question_attempts), 3)

    def test_multiple_question_types_all_question_attempts(self):
        quiz_attempt = QuizAttemptFactory.create(boolean_attempt_count=3, multiple_choice_attempt_count=2)
        self.assertEqual(len(quiz_attempt.all_question_attempts), 5)

    def test_empty_quiz_attempt_score(self):
        quiz_attempt = QuizAttemptFactory.create()
        self.assertEqual(quiz_attempt.score, 0)

    def test_basic_score(self):
        question_set = QuestionSetFactory.create(boolean_question_count=3, displayed_question_count=3)
        quiz_attempt = QuizAttemptFactory.create(quiz=question_set.quiz)
        boolean_attempts = BooleanQuestionAttemptFactory.create_batch(
            3,
            question__question_set__points_per_question=2,
            question__question_set__fault_penalty=0,
            quiz_attempt=quiz_attempt
        )
        self.assertEqual(quiz_attempt.score, 6)