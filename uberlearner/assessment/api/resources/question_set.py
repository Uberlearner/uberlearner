from django.db.models import Q
from django.db.models.query import QuerySet
from tastypie import fields
from assessment.api.authorization.question_set import QuestionSetResourceAuthorization
from assessment.api.resources.quiz import QuizResource
from assessment.models import QuestionSet
from main.api import UberModelResource
from main.api.validation import UberModelValidation


class QuestionSetResource(UberModelResource):
    quiz = fields.ForeignKey(QuizResource, 'quiz')

    class Meta(UberModelResource.Meta):
        resource_name = 'question_sets'
        queryset = QuestionSet.objects.all()
        authorization = QuestionSetResourceAuthorization()
        allowed_methods = ['get', 'post', 'patch', 'put', 'delete']
        validation = UberModelValidation()

    def apply_authorization_limits(self, request, object_list):
        if request.user.is_anonymous():
            return QuerySet.none()
        else:
            # first generate Q filter to check whether the question-set belongs to one of the user's enrollments
            enrollment_q_filter = None
            for enrollment in request.user.enrollments.all():
                enrollment_q_filter = enrollment_q_filter or Q(quiz__course=enrollment.course)
                # filter the object_list by adding in a q_filter to check if the user is the course's instructor
            return object_list.filter(
                enrollment_q_filter or
                Q(quiz__course__instructor__username=request.user.username)
            )