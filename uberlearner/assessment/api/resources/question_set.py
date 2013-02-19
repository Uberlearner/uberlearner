from tastypie import fields
from assessment.api.authorization import QuizRelatedResourceAuthorization
from assessment.api.resources import QuizRelatedResource
from assessment.api.resources.questions.boolean import BooleanQuestionResource
from assessment.api.resources.questions.multiple_choice import MultipleChoiceQuestionResource
from assessment.api.resources.quiz import QuizResource
from assessment.models import QuestionSet
from main.api import UberModelResource


class QuestionSetResource(QuizRelatedResource):
    quiz = fields.ForeignKey(QuizResource, 'quiz')
    boolean_questions = fields.OneToManyField(BooleanQuestionResource, 'booleanquestions', blank=True, null=True)
    multiple_choice_questions = fields.OneToManyField(
        MultipleChoiceQuestionResource,
        'multiplechoicequestions',
        blank=True,
        null=True
    )

    class Meta(QuizRelatedResource.Meta):
        resource_name = 'question_sets'
        queryset = QuestionSet.objects.all()
        _course_navigation_string = 'quiz__course'
        authorization = QuizRelatedResourceAuthorization(course_navigation_string=_course_navigation_string)
