from allauth.account.models import EmailAddress
from django.core.management.base import BaseCommand
from optparse import make_option
from django.template.loader import render_to_string
from courses.models import *
from django.contrib.auth.models import User

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--courses',
            action='store',
            dest='courses',
            default=10,
            help='Adds the specified amount of fake data to the database'
        ), 
    )
    
    args = '<number of entries to be created>'
    help = 'Creates fake data for the Uberlearner project'
            
    def _add_fake_data_to_courses(self, num):
        # create a pool of instructors
        instructor_data = [
            {'first_name': 'first', 'last_name': 'user', 'username': 'first-user', 'email': 'first@aoeu.com'},
            {'first_name': 'second', 'last_name': 'user', 'username': 'second-user', 'email': 'second@aoeu.com'},
            {'first_name': 'third', 'last_name': 'user', 'username': 'third-user', 'email': 'third@aoeu.com'},
            {'first_name': 'fourth', 'last_name': 'user', 'username': 'fourth-user', 'email': 'fourth@aoeu.com'},
            {'first_name': 'fifth', 'last_name': 'user', 'username': 'fifth-user', 'email': 'fifth@aoeu.com'},
        ]
        instructors = []
        for instructor_datum in instructor_data:
            user = User.objects.create_user(instructor_datum['username'], email=instructor_datum['email'], password="aoeu")
            email_address = EmailAddress(user=user, email=instructor_datum['email'], verified=True, primary=True)
            user.first_name = instructor_datum['first_name']
            user.last_name = instructor_datum['last_name']
            user.save()
            email_address.save()
            instructors.append(user)
            
        for idx in xrange(num):
            course = Course(
                instructor=instructors[idx % len(instructor_data)], 
                title='sample title ' + str(idx),
                slug='sample-title-' + str(idx),
                description=('sample description ' + str(idx) + '\t') * 25,
                is_public = True if idx % 2 == 0 else False,
                popularity=0
            )
            course.save()
            self._generate_course_pages(course)

    def _generate_course_pages(self, course):
        for idx in xrange(7):
            Page(
                course=course,
                title='sample page ' + str(idx),
                html=render_to_string('insert_fake_data/page.html', {'number': idx}),
                estimated_effort='123',
                summary="In this section, we will take an in-depth look into foo and bar"
            ).save()
    
    def handle(self, *args, **options):
        courses = int(options['courses'])
        if courses > 0:
            self._add_fake_data_to_courses(courses)