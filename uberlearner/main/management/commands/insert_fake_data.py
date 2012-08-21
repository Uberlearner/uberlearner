import sys
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from courses.models import *
from django.contrib.auth.models import User, UserManager

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
        # create a pool of 5 instructors
        instructor_data = [
            {'first_name': 'crack', 'last_name': 'jack', 'username': 'crack-jack'},
            {'first_name': 'pot', 'last_name': 'head', 'username': 'pot-head'},
            {'first_name': 'shit', 'last_name': 'head', 'username': 'shit-head'},
        ]
        instructors = []
        for instructor_datum in instructor_data:
            user = User.objects.create_user(instructor_datum['username'], email=None, password="aoeu")
            user.first_name = instructor_datum['first_name']
            user.last_name = instructor_datum['last_name']
            user.save()
            instructors.append(user)
            
        for idx in xrange(num):
            course = Course(
                instructor=instructors[idx % len(instructor_data)], 
                title='sample title ' + str(idx),
                slug='sample-title-' + str(idx),
                description='sample description ' + str(idx),
                is_public = True if idx % 2 == 0 else False,
                popularity=idx
            )
            course.save()
    
    def handle(self, *args, **options):
        courses = int(options['courses'])
        if courses > 0:
            self._add_fake_data_to_courses(courses)