from assessment.models import Quiz
from main.api import UberModelResource


class QuizResource(UberModelResource):
    class Meta(UberModelResource.Meta):
        resource_name = 'quizzes'
        queryset = Quiz.objects.all()