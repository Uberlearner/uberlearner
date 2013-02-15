from assessment.api.authorization import QuizRelatedResourceAuthorization
from assessment.api.resources import QuizRelatedResource
from assessment.models import MultipleChoiceQuestion


class MultipleChoiceQuestionResource(QuizRelatedResource):
    class Meta(QuizRelatedResource.Meta):
        resource_name = 'multiple_choice_question'
        queryset = MultipleChoiceQuestion.objects.all()
        _course_navigation_string = 'question_set__quiz__course'
        authorization = QuizRelatedResourceAuthorization(course_navigation_string=_course_navigation_string)
