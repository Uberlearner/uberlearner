from django.core.exceptions import ValidationError
from django.test import TestCase

# The data-structures for the boolean question models is very simple.
# There seems to be no immediate need to test the validation logic for these models.
from assessment.tests.factories import MultipleChoiceQuestionFactory, MultipleChoiceQuestionAttemptFactory, \
    QuestionSetFactory, ChoiceFactory


class MultipleChoiceValidityTests(TestCase):
    def test_correctness(self):
        correct_correctness_values = [0, 0.25, 0.5, 0.75, 1.0]
        sample_incorrect_correctness_values = [-1, 0.1, 1.5]

        for correctness in correct_correctness_values:
            choice = ChoiceFactory.create(correctness=correctness)
            try:
                choice.full_clean()
            except ValidationError:
                self.assertTrue(True, 'Correct correctness value caused validation error')

        for correctness in sample_incorrect_correctness_values:
            choice = ChoiceFactory.create(correctness=correctness)
            self.assertRaises(ValidationError, choice.full_clean)


class SimpleMultipleChoiceQuestionAttemptTests(TestCase):
    def setUp(self):
        self.question_set = QuestionSetFactory.create(points_per_question=2, fault_penalty=1)
        self.question = MultipleChoiceQuestionFactory.create(
            question_set=self.question_set
        )
        self.choices = [
            ChoiceFactory.create(correctness=0, question=self.question),
            ChoiceFactory.create(correctness=0.25, question=self.question),
            ChoiceFactory.create(correctness=1, question=self.question)
        ]

    def test_correct_attempt_marking(self):
        attempt = MultipleChoiceQuestionAttemptFactory.create(question=self.question, answer=self.choices[2])
        self.assertEqual(attempt.score, 2)

    def test_incorrect_attempt_marking(self):
        attempt = MultipleChoiceQuestionAttemptFactory.create(question=self.question, answer=self.choices[0])
        self.assertEqual(attempt.score, -1)

    def test_partially_correct_attempt_marking(self):
        attempt = MultipleChoiceQuestionAttemptFactory.create(question=self.question, answer=self.choices[1])
        self.assertEqual(attempt.score, 0.5)
