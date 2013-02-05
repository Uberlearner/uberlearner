from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
from main.models import TimestampedModel
from django.db import models
from assessment.models import QuestionSet, QuizAttempt

class Question(TimestampedModel):
    """
    This model stores general information regarding a question. The information specific to the particular type
    of question (true/false, multiple-choice etc.) will be stored in other models.
    """
    question_set = models.ForeignKey(QuestionSet, related_name="%(class)ss")
    html = models.TextField(max_length=5000, validators=[MaxLengthValidator(5000)])

    class Meta:
        abstract = True
        order_with_respect_to = 'question_set'
        app_label = 'assessment'

    @property
    def points(self):
        return self.question_set.points_per_question

    @property
    def fault_penalty(self):
        return self.question_set.fault_penalty

class QuestionAttempt(models.Model):
    """
    When a user tries to answer a question, a question attempt instance is created to represent that event.
    """
    quiz_attempt = models.ForeignKey(QuizAttempt, related_name="%(class)ss")

    class Meta:
        abstract = True
        unique_together = ('question', 'quiz_attempt')
        app_label = 'assessment'

    @property
    def score(self):
        raise NotImplementedError()