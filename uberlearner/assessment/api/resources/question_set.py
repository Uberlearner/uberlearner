from tastypie import fields
from assessment.api.authorization import QuizRelatedResourceAuthorization
from assessment.api.resources import QuizRelatedResource
from assessment.api.resources.quiz import QuizResource
from assessment.exceptions import EmptyQuestionSetException
from assessment.models import QuestionSet


class QuestionSetResource(QuizRelatedResource):
    quiz = fields.ForeignKey(QuizResource, 'quiz')

    class Meta(QuizRelatedResource.Meta):
        resource_name = 'question_sets'
        queryset = QuestionSet.objects.all()
        _course_navigation_string = 'quiz__course'
        authorization = QuizRelatedResourceAuthorization(course_navigation_string=_course_navigation_string)

    def dehydrate(self, bundle):
        """
        This method is used to add in the questions field to the resource returned.
        1) If the user is the course instructor, then all the questions are returned
        2) If the user is enrolled in the course, then a set of random questions is returned.
        3) If neither, then the questions field is not present in the response.

        :param bundle: An object consisting of the request, the question_set object and the dictionary (to be
        serialized)
        :return: The same bundle
        """
        question_set = bundle.obj
        course = question_set.quiz.course
        if bundle.request.user:
            try:
                if bundle.request.user == course.instructor:
                    bundle.data['questions'] = question_set.all_questions[:]  # get the actual list not QuerySet
                elif course.is_enrolled(bundle.request.user):
                    bundle.data['questions'] = question_set.random_questions
            except EmptyQuestionSetException as ex:
                bundle.data['questions'] = []

        return super(QuestionSetResource, self).dehydrate(bundle)