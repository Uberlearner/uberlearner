from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from assessment.models.questions import Question, QuestionAttempt


class MultipleChoiceQuestion(Question):
    """
    Questions with many possible answers.
    """
    class Meta(Question.Meta):
        app_label = 'assessment'
        _question_type_code = 'MC'


def validate_correctness(correctness):
    if not correctness in settings.VALID_MULTIPLE_CHOICE_OPTION_CORRECTNESS_VALUES:
        raise ValidationError('Correctness value of option is not one of {0}'.format(
            settings.VALID_MULTIPLE_CHOICE_OPTION_CORRECTNESS_VALUES
        ))

class Choice(models.Model):
    """
    This represents one of the many possible choices of a multiple choice question.
    """
    question = models.ForeignKey(MultipleChoiceQuestion, related_name="choices")
    html = models.TextField()

    # permissible values are 0, 0.25, 0.5, 0.75 and 1
    correctness = models.FloatField(
        default=0,
        help_text="On a scale of 0-1 how correct is this answer. Possible values are {0}".format(
            settings.VALID_MULTIPLE_CHOICE_OPTION_CORRECTNESS_VALUES
        ),
        validators=[validate_correctness]
    )

    class Meta:
        app_label = 'assessment'

class MultipleChoiceQuestionAttempt(QuestionAttempt):
    question = models.ForeignKey(MultipleChoiceQuestion, related_name="attempts")
    answer = models.ForeignKey(Choice, related_name="attempts")

    class Meta:
        app_label = 'assessment'

    @property
    def score(self):
        if self.answer.correctness == 0:
            return -self.question.fault_penalty
        else:
            return self.answer.correctness * self.question.points
