from itertools import chain
import random
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxLengthValidator
from assessment.exceptions import EmptyQuestionSetException
from main.models import TimestampedModel
from django.db import models


class QuestionSet(TimestampedModel):
    """
    This model encapsulates a group of questions of similar characteristics. This is useful if an instructor
    wants to randomly select questions for the quiz out of a question bank while having some control over the
    questions that appear to the student. The question_set can only contain questions of one type. These types
    are mentioned in the QUESTION_TYPES dictionary.
    """

    # Each question-set can only contain questions of one type. The QUESTION_TYPES dictionary contains data related to
    # these question types.
    # The key is a short-code for the question type and will be used in the database itself. The values are a tuple
    # consisting of the human readable form of the question type and the related-manager's name.
    QUESTION_TYPES = {
        u'BOOL': (u'True/False Questions', 'booleanquestions'),
        u'MC': (u'Multiple Choice Questions', 'multiplechoicequestions'),
    }

    quiz = models.ForeignKey('Quiz', related_name="question_sets")
    points_per_question = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    fault_penalty = models.PositiveIntegerField(
        default=0,
        help_text='''Points to be subtracted from the total score in case of incorrect answer. In the interest of the
                  learning experience of the student, it is highly advisable to not penalize for trying. Please use
                  this feature only if you absolutely must.''',
        validators=[MinValueValidator(0)]
    )
    title = models.CharField(max_length=200, blank=True, null=True, validators=[MaxLengthValidator(200)])
    summary = models.TextField(max_length=1000, blank=True, null=True, validators=[MaxLengthValidator(1000)])
    displayed_question_count = models.PositiveSmallIntegerField(
        verbose_name="Number of questions shown to the user",
        blank=True, null=True,
        help_text=(
            "This number dictates the number of questions that will be randomly selected from all the questions"
            "in this question-set when a student takes this quiz. If left blank, all the questions will be selected."
        ),
        validators=[MinValueValidator(1)]
    )
    question_type = models.CharField(
        max_length=4,
        choices=tuple(map(lambda (key, value): (key, value[0]), QUESTION_TYPES.items())),
        default='MC'
    )

    class Meta:
        order_with_respect_to = 'quiz'
        app_label = 'assessment'

    def __unicode__(self):
        return u"{quiz} - question-set - {title}".format(
            quiz=str(self.quiz),
            title=self.title or u"Untitled"
        )

    @property
    def _question_model_related_manager_name(self):
        return self.QUESTION_TYPES[self.question_type][1]

    def clean(self):
        """
        1) Make sure that fault_penalty is not greater than points_per_question
        """
        if self.fault_penalty > self.points_per_question:
            raise ValidationError('Fault penalty cannot be greater than points_per_question')

        return super(QuestionSet, self).clean()

    @property
    def real_question_count(self):
        """
        This is the number of questions attached to this question in the database. This number can be (and should
        ideally be) greater than the displayed_question_count.
        """
        return getattr(self, self._question_model_related_manager_name).count()

    @property
    def question_count(self):
        """
        This is the number of questions that the student will be asked when attempting this question_set. It is essentially
        the minimum of the displayed_question_count and the real_question_count
        """
        return min(self.real_question_count, self.displayed_question_count)

    @property
    def points(self):
        """
        @return: The total number of points that can be earned through this question set.
        """
        question_count = self.real_question_count
        if question_count < self.displayed_question_count:
            return question_count * self.points_per_question
        else:
            return self.displayed_question_count * self.points_per_question

    @property
    def all_questions(self):
        return getattr(self, self._question_model_related_manager_name).all()

    @property
    def random_questions(self):
        """
        Returns a list of random questions from the question-set equal in number to the number of questions
        that should be displayed to the student taking the quiz. This number is derived from the question_count
        property of the question-set.

        :return: A list
        :raise: If the question_set doesn't have any questions
        """
        questions = self.all_questions.order_by('?')[:self.question_count]

        if questions is None or len(questions) == 0:
            raise EmptyQuestionSetException('Could not draw questions from empty question set')

        return questions

    @models.permalink
    def get_resource_uri(self, url_name='api_dispatch_detail'):
        # avoid circular import
        from assessment.api.resources.question_set import QuestionSetResource
        from uberlearner.urls import v1_api

        return (url_name, (), {
            'resource_name': QuestionSetResource._meta.resource_name,
            'api_name': v1_api.api_name,
            'pk': self.id
        })