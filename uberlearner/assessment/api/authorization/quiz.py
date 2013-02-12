from assessment.api.authorization import QuizRelatedResourceAuthorization
from courses.models import Course


class QuizResourceAuthorization(QuizRelatedResourceAuthorization):
    def get_course(self, obj=None, data=None):
        if obj is not None and hasattr(obj, 'course'):
            return obj.course
        elif data is not None:
            return self.get_object(data['course'], object_class=Course)
        else:
            return None
