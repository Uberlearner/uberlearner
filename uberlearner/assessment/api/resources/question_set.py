from assessment.models import QuestionSet
from main.api import UberModelResource


class QuizResource(UberModelResource):
    class Meta(UberModelResource.Meta):
        resource_name = 'question_sets'
        queryset = QuestionSet.objects.all()
