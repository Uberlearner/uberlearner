import factory
from accounts.tests.factories import UserFactory
from courses.tests.factories import CourseFactory
from assessment.models import (Quiz, QuestionSet, QuizAttempt, BooleanQuestion, BooleanQuestionAttempt,
                               MultipleChoiceQuestion, MultipleChoiceQuestionAttempt, Question, Choice,
                               QuestionAttempt)


class QuizFactory(factory.Factory):
    FACTORY_FOR = Quiz

    course = factory.SubFactory(CourseFactory)
    summary = 'Summary of a test quiz'
    title = 'Title of a test quiz'


class QuestionSetFactory(factory.Factory):
    FACTORY_FOR = QuestionSet

    quiz = factory.SubFactory(QuizFactory)
    points_per_question = 2
    fault_penalty = 1
    title = 'Test question set'
    summary = 'Test summary of test question set'
    displayed_question_count = 1

    @factory.post_generation(extract_prefix='boolean_question_count')
    def generate_boolean_questions(self, create, extracted, **kwargs):
        """
        Generates the given number of boolean questions for the question-set.

        If the QuestionSetFactory instance is created with the boolean_question_count parameter,
        this method will be automatically called.

        :param create: Whether the objects are to be created (saved)
        :param extracted: The number of questions to be created
        :param kwargs:
        """
        question_count = extracted
        if question_count is None:
            return

        if create:
            BooleanQuestionFactory.create_batch(question_count, question_set=self)
        else:
            BooleanQuestionFactory.build_batch(question_count, question_set=self)

    @factory.post_generation(extract_prefix='multiple_choice_question_count')
    def generate_multiple_choice_questions(self, create, extracted, **kwargs):
        """
        Generates the given number of multiple-choice questions for the question-set.

        If the QuestionSetFactory instance is created with the multiple_choice_question_count parameter,
        this method will automatically generate the required number of multiple-choice-questions.

        :param create: Whether the objects are to be created (saved)
        :param extracted: The number of questions to be created
        :param kwargs:
        """
        question_count = extracted
        if question_count is None:
            return

        if create:
            MultipleChoiceQuestionFactory.create_batch(question_count, question_set=self)
        else:
            MultipleChoiceQuestionFactory.build_batch(question_count, question_set=self)


class QuizAttemptFactory(factory.Factory):
    FACTORY_FOR = QuizAttempt

    user = factory.SubFactory(UserFactory)
    quiz = factory.SubFactory(QuizFactory)

    @factory.post_generation(extract_prefix='boolean_attempt_count')
    def generate_boolean_attempts(self, create, extracted, **kwargs):
        attempt_count = extracted
        if attempt_count is None:
            return

        if create:
            BooleanQuestionAttemptFactory.create_batch(attempt_count, quiz_attempt=self)
        else:
            BooleanQuestionAttemptFactory.build_batch(attempt_count, quiz_attempt=self)

    @factory.post_generation(extract_prefix='multiple_choice_attempt_count')
    def generate_multiple_choice_attempts(self, create, extracted, **kwargs):
        attempt_count = extracted
        if attempt_count is None:
            return

        if create:
            MultipleChoiceQuestionAttemptFactory.create_batch(attempt_count, quiz_attempt=self)
        else:
            MultipleChoiceQuestionAttemptFactory.build_batch(attempt_count, quiz_attempt=self)


class QuestionFactory(factory.Factory):
    question_set = factory.SubFactory(QuestionSetFactory)
    html = "<p>Test generic type question</p>"


class QuestionAttemptFactory(factory.Factory):
    quiz_attempt = factory.SubFactory(QuizAttemptFactory)


class BooleanQuestionFactory(QuestionFactory):
    FACTORY_FOR = BooleanQuestion

    correct_answer = False


class BooleanQuestionAttemptFactory(QuestionAttemptFactory):
    FACTORY_FOR = BooleanQuestionAttempt

    question = factory.SubFactory(BooleanQuestionFactory)
    answer = False


class MultipleChoiceQuestionFactory(QuestionFactory):
    FACTORY_FOR = MultipleChoiceQuestion


class ChoiceFactory(factory.Factory):
    FACTORY_FOR = Choice

    question = factory.SubFactory(MultipleChoiceQuestionFactory)
    html = '<b>Test choice</b>'
    correctness = 0


class MultipleChoiceQuestionAttemptFactory(QuestionAttemptFactory):
    FACTORY_FOR = MultipleChoiceQuestionAttempt

    question = factory.SubFactory(MultipleChoiceQuestionFactory)
    answer = factory.SubFactory(ChoiceFactory)