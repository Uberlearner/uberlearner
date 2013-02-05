from django.test import TestCase

# The data-structures for the boolean question models is very simple.
# There seems to be no immediate need to test the validation logic for these models.
from assessment.tests.factories import BooleanQuestionFactory, BooleanQuestionAttemptFactory, QuestionSetFactory

class SimpleBooleanQuestionAttemptTests(TestCase):
    def setUp(self):
        self.question_set = QuestionSetFactory.create(points_per_question=2, fault_penalty=1)
        self.question = BooleanQuestionFactory.create(question_set=self.question_set, correct_answer=False)

    def test_correct_attempt_marking(self):
        attempt = BooleanQuestionAttemptFactory.create(question=self.question, answer=False)
        self.assertEqual(attempt.score, 2)

    def test_incorrect_attempt_marking(self):
        attempt = BooleanQuestionAttemptFactory.create(question=self.question, answer=True)
        self.assertEqual(attempt.score, -1)