from django.core.validators import MinValueValidator, MaxLengthValidator
from assessment.exceptions import EmptyQuizAttemptedException
from question_set import QuestionSet
from quiz_attempt import QuizAttempt
from courses.models import Course
from main.models import TimestampedModel
from django.db import models


class Quiz(TimestampedModel):
    """
    A quiz in a course is technically just a set of questions and some meta-data.

    In reality however, there is an intermediate model called question_set that encapsulates a set
    of questions with common characteristics. This is not only useful for grouping of questions, but
    also for randomly selecting a subset of the questions to test the student on while having some amount
    of control over the types of questions that appear to the student.
    """
    GRADING_METHODS = (
        ('highest', 'Highest Grade'),
        ('average', 'Average Grade'),
        ('first', 'First Attempt'),
        ('last', 'Last Attempt')
    )

    class Meta:
        app_label = 'assessment'

    course = models.ForeignKey(Course, related_name="quizzes")
    # for some reason, max_length by itself won't raise an exception if length is exceeded
    summary = models.TextField(max_length=1000, blank=True, null=True,
                               validators=[MaxLengthValidator(1000)])
    title = models.CharField(max_length=200, validators=[MaxLengthValidator(200)])

    grading_method = models.CharField(choices=GRADING_METHODS, default='highest', max_length=7)

    # re-attempt behaviour
    attempts_allowed = models.PositiveSmallIntegerField(
        verbose_name="Number of attempts allowed", blank=True, null=True,
        help_text="If no value is set, then infinite attempts will be allowed",
        validators=[MinValueValidator(1)]
    )
    reattempt_interval = models.PositiveIntegerField(
        verbose_name="Minimum time between attempts", blank=True, default=0,
        help_text="In minutes"
    )

    def __unicode__(self):
        return u"{title} ({course})".format(
            title=self.title,
            course=str(self.course)
        )

    @property
    def question_count(self):
        """
        Returns the number of questions that the student will see during attempts.
        """
        count = 0
        for question_set in self.question_sets.all():
            count += question_set.question_count
        return count

    @property
    def real_question_count(self):
        """
        Returns the number of questions that are stored in the database. When a student attempts the quiz, a subset
        of these questions (equal in number to the property question_count) will be shown to the student.
        """
        count = 0
        for question_set in self.question_sets.all():
            count += question_set.real_question_count
        return count

    @property
    def points(self):
        """
        Returns the total points for the quiz by adding the points from all the question sets

        :return: The sum of the points from all the question sets.
        """
        return sum(map(
            lambda question_set: question_set.points,
            self.question_sets.all()
        ))

    def generate_question_set(self, create=True, *args, **kwargs):
        """
        Generates a question set that is attached to this quiz through foreign key.
        :param create: Whether the question set is to be created (saved).
        :param args: The args to use for creation of the question-set
        :param kwargs: The kwargs to use for creation of the question-set
        """
        question_set = QuestionSet(*args, **kwargs)
        question_set.quiz = self
        if create:
            question_set.save()
        return question_set

    def generate_attempt(self, user, create=True):
        """
        Creates an attempt instance that is attached to this quiz.
        :param user: The user attempting the quiz
        :param create: Whether the attempt is to be created (saved)
        """
        if self.question_count == 0:
            raise EmptyQuizAttemptedException()

        attempt = QuizAttempt(user=user, quiz=self)
        if create:
            attempt.save()
        return attempt