from django.db.models import Q
from django.db.models.query import QuerySet
from tastypie import fields
from assessment.api.authorization.quiz import QuizResourceAuthorization
from assessment.models import Quiz
from courses.api import CourseResource
from main.api import UberModelResource
from main.api.validation import UberModelValidation


class QuizResource(UberModelResource):
    course = fields.ForeignKey(CourseResource, 'course')
    question_sets = fields.OneToManyField(
        'assessment.api.resources.question_set.QuestionSetResource',
        'question_sets',
        related_name='quiz',
        blank=True,
        null=True
    )

    class Meta(UberModelResource.Meta):
        resource_name = 'quizzes'
        queryset = Quiz.objects.all()
        authorization = QuizResourceAuthorization()
        allowed_methods = ['get', 'post', 'patch', 'put', 'delete']
        validation = UberModelValidation()

    def apply_authorization_limits(self, request, object_list):
        if request.user.is_anonymous():
            return QuerySet.none()
        else:
            # first generate Q filter to check whether the quiz belongs to one of the user's enrollments
            enrollment_q_filter = None
            for enrollment in request.user.enrollments.all():
                enrollment_q_filter = enrollment_q_filter or Q(course=enrollment.course)
                # filter the object_list by adding in a q_filter to check if the user is the course's instructor
            return object_list.filter(
                enrollment_q_filter or
                Q(course__instructor__username=request.user.username)
            )