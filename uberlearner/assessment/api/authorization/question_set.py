from assessment.api.authorization import QuizRelatedResourceAuthorization
from assessment.models import Quiz


class QuestionSetResourceAuthorization(QuizRelatedResourceAuthorization):
    def get_course(self, obj=None, data=None):
        if obj is not None and hasattr(obj, 'quiz') and obj.quiz is not None and hasattr(obj.quiz, 'course'):
            return obj.quiz.course
        elif data is not None:
            quiz = self.get_object(data['quiz'], object_class=Quiz)
            return quiz.course
        else:
            return None