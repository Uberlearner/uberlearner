import factory
from courses.models import Course, Instructor, Page, Enrollment
from accounts.tests.factories import UserFactory

class InstructorFactory(factory.Factory):
    FACTORY_FOR = Instructor

    user = factory.SubFactory(UserFactory, username="testinstructor")

class CourseFactory(factory.Factory):
    FACTORY_FOR = Course

    instructor = factory.SubFactory(UserFactory)
    title = 'Test course'
    slug = 'test-course'
    description = """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut
    labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip
    ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat
    nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id
    est laborum."""

    is_public = True
    deleted = False

    @classmethod
    def _prepare(cls, create, **kwargs):
        student = UserFactory()
        course = super(CourseFactory, cls)._prepare(create, **kwargs)
        enrollment = EnrollmentFactory(student=student, course=course)
        return course

class EnrollmentFactory(factory.Factory):
    FACTORY_FOR = Enrollment

    student = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)

class PageFactory(factory.Factory):
    FACTORY_FOR = Page

    course = factory.SubFactory(CourseFactory)
    title = 'Test course'
    summary = 'Test course\'s test summary'
    estimated_effort = 23 #minutes
    html = """<p>Content of this awesome page!</p>"""