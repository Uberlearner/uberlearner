from django.db.models import Q
from main.api import UberModelResource
from main.api.validation import UberModelValidation


class QuizRelatedResource(UberModelResource):
    """
    This is an abstract resource that all the resources related the the quizzes, their question sets and their
    corresponding questions inherit from. Since the permission structure of these resources is common, the logic
    for those commonalities has been extracted into this resource.
    """
    class Meta(UberModelResource.Meta):
        allowed_methods = ['get', 'post', 'patch', 'put', 'delete']
        validation = UberModelValidation()

    def apply_authorization_limits(self, request, object_list):
        """
        This method applies the authorization limits for a user based on the _course_navigation_string mentioned in the
        Meta class of the resource. This has to provide by every resource that inherits from this class. This is used
        to generated Q filters for filtering based on the course.
        """
        if request.user.is_anonymous():
            return object_list.none()
        else:
            # first generate Q filter to check whether the quiz belongs to one of the user's enrollments
            enrollment_q_filter = None
            for enrollment in request.user.enrollments.all():
                enrollment_q_filter = enrollment_q_filter or Q(**{self.Meta._course_navigation_string: enrollment.course})
                # filter the object_list by adding in a q_filter to check if the user is the course's instructor
            username_navigation_string = "{0}__instructor__username".format(self.Meta._course_navigation_string)
            return object_list.filter(
                enrollment_q_filter or
                Q(**{username_navigation_string: request.user.username})
            )
