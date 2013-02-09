from itertools import chain
from django.contrib.auth.models import User
from django.db import models


class QuizAttempt(models.Model):
    """
    This is essentially a combination of the various attempts for each of the questions in the quiz
    """
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(User, related_name="quiz_attempts")
    quiz = models.ForeignKey('Quiz', related_name="attempts")

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
    def all_question_attempts(self):
        """
        Returns all the question attempts this quiz attempt is related to.
        """
        boolean_question_attempts = self.booleanquestionattempts.all()
        multiple_choice_question_attempts = self.multiplechoicequestionattempts.all()
        return list(chain(boolean_question_attempts, multiple_choice_question_attempts))

    @property
    def score(self):
        """
        Returns the total score attained by the student attempting the quiz.
        """
        return sum(map(lambda attempt: attempt.score, self.all_question_attempts))
