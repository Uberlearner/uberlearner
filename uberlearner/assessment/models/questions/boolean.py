from django.db import models
from assessment.models.questions import Question, QuestionAttempt

class BooleanQuestion(Question):
    """
    True/False type questions.
    """
    correct_answer = models.BooleanField()

    class Meta:
        app_label = 'assessment'


class BooleanQuestionAttempt(QuestionAttempt):
    question = models.ForeignKey(BooleanQuestion, related_name="attempts")
    answer = models.BooleanField()

    class Meta:
        app_label = 'assessment'

    @property
    def score(self):
        if self.answer == self.question.correct_answer:
            return self.question.points
        else:
            return -self.question.fault_penalty