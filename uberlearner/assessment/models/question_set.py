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
    questions that appear to the student.

    For example, if the instructor wanted to test the students using a quiz containing 2 true/false quizzes and
    2 multiple choice quizzes, they could create 2 question-sets: one containing 4 true/false questions and
    another one containing 4 multiple-choice questions. Then these question-sets could be configured to contribute
    2 random questions each every time a quiz was shown to the user.
    """
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

    QUESTION_MODEL_RELATED_MANAGER_NAMES = ['booleanquestions', 'multiplechoicequestions']

    class Meta:
        order_with_respect_to = 'quiz'
        app_label = 'assessment'

    def __unicode__(self):
        return u"{quiz} - question-set - {title}".format(
            quiz=str(self.quiz),
            title=self.title or u"Untitled"
        )

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
        count = 0
        for related_manager_name in self.QUESTION_MODEL_RELATED_MANAGER_NAMES:
            count += getattr(self, related_manager_name).all().count()
        return count

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
        boolean_questions = self.booleanquestions.all()
        multiple_choice_questions = self.multiplechoicequestions.all()
        return list(chain(boolean_questions, multiple_choice_questions))

    @property
    def random_questions(self):
        """
        Returns a list of random questions from the question-set equal in number to the number of questions
        that should be displayed to the student taking the quiz. This number is derived from the question_count
        property of the question-set.

        :return: A list
        :raise: If the question_set doesn't have any questions
        """
        # TODO: Optimize method get_random_questions
        # The current approach of querying the various types of questions and combining them into a randomly
        # ordered list is quite inefficient. This could be moved into a raw query later if the need arises.
        questions = self.all_questions
        random.shuffle(questions)

        if questions is None or len(questions) == 0:
            raise EmptyQuestionSetException('Could not draw questions from empty question set')

        return questions[:self.question_count]