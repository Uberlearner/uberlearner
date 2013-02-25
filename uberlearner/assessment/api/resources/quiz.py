from tastypie import fields
from assessment.api.authorization import QuizRelatedResourceAuthorization
from assessment.api.resources import QuizRelatedResource
from assessment.models import Quiz
from courses.api import CourseResource


class QuizResource(QuizRelatedResource):
    course = fields.ForeignKey(CourseResource, 'course')
    question_sets = fields.OneToManyField(
        'assessment.api.resources.question_set.QuestionSetResource',
        'question_sets',
        related_name='quiz',
        blank=True,
        null=True
    )

    class Meta(QuizRelatedResource.Meta):
        resource_name = 'quizzes'
        queryset = Quiz.objects.all()
        _course_navigation_string = 'course'
        authorization = QuizRelatedResourceAuthorization(course_navigation_string=_course_navigation_string)

    def dehydrate(self, bundle):
        """
        Modifies the bundle data just before it serializes to ensure that:
        1) Only the instructor can see the question_sets directly
        2) The question-count and points show up in the response

        :param bundle: The tastypie object containing the quiz object, the dictionary to be serialized, the request etc.
        :return: The bundle
        """
        if bundle.request.user != bundle.obj.course.instructor:
            del bundle.data['question_sets']
        bundle.data['question_count'] = bundle.obj.question_count
        bundle.data['points'] = bundle.obj.points
        return super(QuizResource, self).dehydrate(bundle)