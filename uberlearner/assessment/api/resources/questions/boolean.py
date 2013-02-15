from assessment.api.authorization import QuizRelatedResourceAuthorization
from assessment.api.resources import QuizRelatedResource
from assessment.models import BooleanQuestion


class BooleanQuestionResource(QuizRelatedResource):
    class Meta(QuizRelatedResource.Meta):
        resource_name = 'boolean_question'
        queryset = BooleanQuestion.objects.all()
        _course_navigation_string = 'question_set__quiz__course'
        authorization = QuizRelatedResourceAuthorization(course_navigation_string=_course_navigation_string)
