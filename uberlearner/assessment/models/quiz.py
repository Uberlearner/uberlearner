from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxLengthValidator
from assessment.exceptions import EmptyQuizAttemptedException
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
    summary = models.TextField(max_length=1000, blank=True, null=True,
        validators=[MaxLengthValidator(1000)]) #for some reason, max_length by itself won't raise an exception if length is exceeded
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
        return sum(map(
            lambda question_set: question_set.points,
            self.question_sets.all()
        ))

    def generate_question_set(self, create=True, *args, **kwargs):
        """
        Generates a question set that is attached to this quiz through foreign key.
        """
        question_set = QuestionSet(*args, **kwargs)
        question_set.quiz = self
        if create:
            question_set.save()
        return question_set

    def generate_attempt(self, user, create=True):
        """
        Creates an attempt instance that is attached to this quiz.
        """
        if self.question_count == 0:
            raise EmptyQuizAttemptedException()

        attempt = QuizAttempt(user=user, quiz=self)
        if create:
            attempt.save()
        return attempt

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
    quiz = models.ForeignKey(Quiz, related_name="question_sets")
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
        help_text="""This number dictates the number of questions that will be randomly selected from all the questions
                  in this question-set when a student takes this quiz. If left blank, all the questions will be selected.""",
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

class QuizAttempt(models.Model):
    """
    This is essentially a combination of the various attempts for each of the questions in the quiz
    """
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(User, related_name="quiz_attempts")
    quiz = models.ForeignKey(Quiz, related_name="attempts")

    class Meta:
        unique_together = ('user', 'quiz', 'timestamp')
        app_label = 'assessment'

    def __unicode__(self):
        return "Quiz attempt for '{quiz}' by '{user}' at {time}".format(
            quiz=str(self.quiz),
            user=str(self.user),
            time=str(self.timestamp)
        )

    @property
    def score(self):
        raise NotImplementedError()