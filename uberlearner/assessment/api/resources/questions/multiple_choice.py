from assessment.models import MultipleChoiceQuestion
from main.api import UberModelResource


class MultipleChoiceQuestionResource(UberModelResource):
    class Meta(UberModelResource.Meta):
        resource_name = 'multiple_choice'
        queryset = MultipleChoiceQuestion.objects.all()