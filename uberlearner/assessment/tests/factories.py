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

class QuizAttemptFactory(factory.Factory):
    FACTORY_FOR = QuizAttempt

    user = factory.SubFactory(UserFactory)
    quiz = factory.SubFactory(QuizFactory)

class QuestionFactory(factory.Factory):
    FACTORY_FOR = Question

    question_set = factory.SubFactory(QuestionSetFactory)
    html = "<p>Test generic type question</p>"

class QuestionAttemptFactory(factory.Factory):
    FACTORY_FOR = QuestionAttempt

    question = factory.SubFactory(QuestionFactory)
    quiz_attempt = factory.SubFactory(QuizAttemptFactory)

class BooleanQuestionFactory(QuestionFactory):
    FACTORY_FOR = BooleanQuestion

    correct_answer = False

class BooleanQuestionAttemptFactory(QuestionAttemptFactory):
    FACTORY_FOR = BooleanQuestionAttempt

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

    answer = factory.SubFactory(ChoiceFactory)