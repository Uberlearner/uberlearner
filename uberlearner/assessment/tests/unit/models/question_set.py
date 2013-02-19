from itertools import chain
from django.core.exceptions import ValidationError
from django.test import TestCase
from assessment.exceptions import EmptyQuestionSetException
from assessment.tests.factories import QuestionSetFactory, BooleanQuestionFactory, MultipleChoiceQuestionFactory


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

    def test_that_question_set_cannot_contain_multiple_question_types(self):
        question_set = QuestionSetFactory.create(question_type='BOOL', boolean_question_count=5)
        mc_question = MultipleChoiceQuestionFactory.build(question_set=question_set)
        self.assertRaises(ValidationError, mc_question.full_clean)


class QuestionSetPropertyTests(TestCase):
    def test_empty_question_set_points(self):
        question_set = QuestionSetFactory.create()
        self.assertEqual(question_set.points, 0)

    def test_question_starved_question_set_points(self):
        question_set = QuestionSetFactory.create(points_per_question=2, displayed_question_count=3, question_type='BOOL')
        questions = BooleanQuestionFactory.create(question_set=question_set)
        self.assertEqual(question_set.points, 2)

    def test_full_question_set_points(self):
        question_set = QuestionSetFactory.create(points_per_question=2, displayed_question_count=3, question_type='BOOL')
        questions = BooleanQuestionFactory.create_batch(3, question_set=question_set)
        self.assertEqual(question_set.points, 6)

    def test_over_filled_question_set_points(self):
        question_set = QuestionSetFactory.create(points_per_question=2, displayed_question_count=3, question_type='BOOL')
        questions = BooleanQuestionFactory.create_batch(5, question_set=question_set)
        self.assertEqual(question_set.points, 6)

    def test_all_questions_boolean_only(self):
        question_set = QuestionSetFactory.create(question_type='BOOL')
        boolean_questions = BooleanQuestionFactory.create_batch(3, question_set=question_set)
        self.assertEqual(set(question_set.all_questions), set(boolean_questions))

    def test_all_questions_multiple_choice_only(self):
        question_set = QuestionSetFactory.create(question_type='MC')
        multiple_choice_questions = MultipleChoiceQuestionFactory.create_batch(3, question_set=question_set)
        self.assertEqual(set(question_set.all_questions), set(multiple_choice_questions))

    def test_empty_question_set_random_questions(self):
        #: :type: QuestionSet
        question_set = QuestionSetFactory.create()
        try:
            random_questions = question_set.random_questions
            self.fail('Did not raise exception when random_questions were requested from empty question set')
        except EmptyQuestionSetException as ex:
            pass

    def test_question_starved_question_set_random_questions(self):
        #: :type: QuestionSet
        question_set = QuestionSetFactory.create(
            displayed_question_count=5,
            boolean_question_count=1,
            question_type='BOOL'
        )
        random_questions = question_set.random_questions
        self.assertEqual(set(random_questions), set(question_set.all_questions))
        self.assertGreater(question_set.displayed_question_count, len(random_questions))

    def test_full_question_set_random_questions(self):
        #: :type: QuestionSet
        question_set = QuestionSetFactory.create(
            displayed_question_count=5,
            boolean_question_count=5,
            question_type='BOOL'
        )
        random_questions = question_set.random_questions
        self.assertEqual(set(random_questions), set(question_set.all_questions))
        self.assertEqual(len(random_questions), question_set.displayed_question_count)

    def test_over_filled_question_set_random_questions(self):
        #: :type: QuestionSet
        question_set = QuestionSetFactory.create(
            displayed_question_count=3,
            boolean_question_count=5,
            question_type='BOOL'
        )
        random_questions = question_set.random_questions
        all_questions = question_set.all_questions
        self.assertEqual(len(random_questions), question_set.displayed_question_count)
        self.assertGreater(len(all_questions), len(random_questions))
        self.assertTrue(frozenset(random_questions).issubset(frozenset(all_questions)))

    def test_randomness_of_questions(self):
        """
        Technically, a test of randomness of questions is impossible. But it is possible to create a test
        such that the probability of it passing is exceedingly high.
        """
        question_set = QuestionSetFactory.create(
            displayed_question_count=3,
            boolean_question_count=100,
            question_type='BOOL'
        )
        previous_questions = None
        for test_run in xrange(10):
            random_questions = question_set.random_questions
            if previous_questions is not None:
                if frozenset(previous_questions) != frozenset(random_questions):
                    break
            previous_questions = random_questions
        else:
            # if the loop was ended because of exhaustion, then the test failed
            self.fail('Random selections seem to be too similar. This could be just a very improbable event - try running'
                      'the test again.')
