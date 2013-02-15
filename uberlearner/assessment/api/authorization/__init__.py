from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation
from courses.models import Course
from main.api.authorization import UberAuthorization


class QuizRelatedResourceAuthorization(UberAuthorization):
    """
    This authorization class is for all resources related to the design of a quiz. These resources include:
    1) quizzes
    2) question-sets
    3) questions

    This works because the same permissions apply to all these objects. For example, if a user has
    permissions to create a quiz, the same user will also have the permissions to create a question-set
    and its corresponding questions.

    Since all the permissions depend on accessing the course related to the object (quiz, question-set or any
    type of question), the method get_course has to be defined by all the subclasses.
    """

    def __init__(self, course_navigation_string):
        if not course_navigation_string:
            raise ValueError('Course navigation string is required')
        self.course_navigation_string = course_navigation_string

    def get_course_from_object(self, obj):
        """
        Gets the course object given the object corresponding to the model backing the resource this authorization
        is being used for.

        :param obj: The object of concern
        :raise: NotImplementedError because the subclasses have to implement this method
        """
        course = None
        attribute_list = self.course_navigation_string.split('__')
        try:
            current_node = obj
            for attribute_name in attribute_list:
                current_node = getattr(current_node, attribute_name)
            course = current_node
        finally:
            return course

    def get_course_from_data(self, data):
        """

        :param data: A dictionary containing the resource uri of the course (attached to the key 'course')
        :return: The course object
        """
        course = None
        try:
            course = self.get_object(data['course'], object_class=Course)
        except (KeyError, AttributeError) as ex:
            pass
        finally:
            return course

    def get_course(self, obj=None, data=None):
        """
        Returns the course object given either the relevant object (quiz, question-set or any type of question) or
        a data dictionary containing the course resource uri (corresponding to the 'course' key) or both.
        In the case of both pieces of data being present, the obj is given precedence.

        Note: One of the methods this method depends on is the get_course_from_object method. This method has to be
        implemented by all the subclasses.

        :param obj: The object of concern
        :param data: The data from the request
        """
        if obj is not None:
            return self.get_course_from_object(obj)
        elif data is not None:
            return self.get_course_from_data(data)
        else:
            return None

    def is_get_list_authorized(self, user):
        """
        Checks the authorization of the get requests for a list of objects.

        :param user: The user who made the request
        :return: True if the user has authorization, False otherwise
        """
        # all authenticated users are allowed
        # the apply_authorization_limits method of the resource should take care of filtering the querysets
        return True

    def is_get_object_authorized(self, obj, user):
        """
        Checks the authorization of the get requests for a particular object

        :param obj: The object of concern 
        :param user: The user who made the request 
        :return: True if the user has authorization, False otherwise
        """
        course = self.get_course(obj)
        if user == course.instructor:
            return True
        elif course.enrollments.filter(student=user).exists():
            return True
        else:
            return False

    def is_get_method_authorized(self, obj, user):
        """
        Checks the authorization of a get request.
        
        :param obj: The object of concern
        :param user: The user who made the request 
        :return: True if the user has authorization, False otherwise
        """
        if obj is not None:
            return self.is_get_object_authorized(obj, user)
        else:
            return self.is_get_list_authorized(user)

    def is_post_method_authorized(self, obj, user, data):
        """
        Checks the authorization of a post request.

        :param obj: The object of concern
        :param user: The user who made the request 
        :param data: The POST data dictionary
        :return: True if the user has authorization, False otherwise
        :raise: ObjectDoesNotExist
        """
        course = self.get_course(obj, data)
        if course is None:
            raise ObjectDoesNotExist('Could not get the required course')

        return course.instructor == user

    def are_put_and_patch_methods_authorized(self, obj, user, data):
        """
        Checks the authorization of both put and patch methods

        :param obj: The object of concern
        :param user: The user who made the request 
        :param data: 
        :return: True if the user has authorization, False otherwise

        :raise:
        SuspiciousOperation if the course in the request data is not the same as the course the quiz belongs to.
        ObjectDoesNotExist if the path of the request does not refer to any valid object
        """
        if obj is None:
            return False

        # we don't want to give the get_course method the data dict so we could check consistency.
        # also, the object has to be provided through the path of the request
        course = self.get_course(obj)
        if course is None:
            raise ObjectDoesNotExist('Please check the path of the request')
        if 'course' in data and data['course'] != course:
            raise SuspiciousOperation('The quiz does not belong to the course mentioned in the request data')

        return user.pk == course.instructor.pk

    def is_delete_method_authorized(self, obj, user):
        """

        :param obj: The object of concern
        :param user: The user who made the request 
        :return: True if the user has authorization, False otherwise
        """
        if obj is None:
            return False

        course = self.get_course(obj)
        return user.pk == course.pk

    def _get_request_data(self, request):
        if request.method == 'POST':
            data = request.raw_post_data
            data = self.resource_meta.serializer.deserialize(data)
            return data
        else:
            return {}

    def is_authorized(self, request, obj=None):
        """

        :param request: 
        :param obj: The object of concern
        :return: True if the user has authorization, False otherwise
        """
        # since an unauthorized user cannot do anything with these resources, it makes for easy pickings
        if not request.user or (request.user and request.user.is_anonymous()):
            return False

        if obj is None:
            obj = self.get_object(request.path)  # it is possible for the object to still be None

        request_data = self._get_request_data(request)

        if request.method == 'GET':
            return self.is_get_method_authorized(obj, request.user)
        elif request.method == 'POST':
            return self.is_post_method_authorized(obj, request.user, request_data)
        elif request.method == 'PUT' or request.method == 'PATCH':
            return self.are_put_and_patch_methods_authorized(obj, request.user, request_data)
        elif request.method == 'DELETE':
            return self.is_delete_method_authorized(obj, request.user)
        else:
            return False
