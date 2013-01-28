from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from tastypie.authorization import Authorization
import types
from courses.models import Course

class CourseAuthorization(Authorization):
    """
    Handles authorization for the course resources.
    """
    def is_authorized(self, request, object=None):
        """
        If the request is GET and the object has a is_public attribute
        that is true, then the user is authorized.
        If the user is a super-user, then the user is authorized.
        If the object is a course, or if the object has a course
        associated with it, and the user is the instructor, then
        the course is authorized.
        """
        if request.user.is_superuser:
            return True

        if not object:
            # if the object is unavailable, then leave the authorization to the apply_limits method
            # or to the over-rides of this method
            return True

        if request.method == 'GET' and hasattr(object, 'is_public'):
            is_public = False
            obj_visibility_attr = object.is_public
            if isinstance(obj_visibility_attr, types.FunctionType):
                is_public = obj_visibility_attr()
            elif isinstance(obj_visibility_attr, types.BooleanType):
                is_public = obj_visibility_attr
            else:
                raise ImproperlyConfigured('The is_public method of {obj} should either be a function or a boolean'.format(
                    obj=object
                ))
            return is_public
        else:
            course = None
            if isinstance(object, Course):
                course = object
            elif hasattr(object, 'course'):
                course = getattr(object, 'course')
            elif hasattr(object, 'get_course') and isinstance(getattr(object, 'get_course'), types.FunctionType):
                course = getattr(object, 'get_course')()
            if course and course.instructor == request.user:
                return True
            else:
                return False
    """
    def apply_limits(self, request, object_list):
        if request.user.is_superuser:
            return object_list
        elif request.method == 'GET':
            return object_list.filter(Q(course__is_public=True) | Q(course__instructor__id=request.user.id))
        else:
            return object_list.filter(course__instructor__id=request.user.id)
    """