from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from main.models import TimestampedModel
################################
# Main models
################################
        
class Instructor(models.Model):
    """
    This model encapsulates the various properties of a user who has signed
    on to be an instructor.
    """
    user = models.OneToOneField(User)
    rating = models.FloatField()
    popularity = models.PositiveIntegerField()
    
class Course(TimestampedModel):
    """
    This model encapsulates the various parameters of a course.
    """
    instructor = models.ForeignKey(Instructor)
    # TEACHING ASSISTANTS AND TRANSLATORS WILL BE IMPLEMENTED LATER
    # teaching_assistants = models.ManyToManyField(Instructor)
    # translators = models.ManyToManyField(Translator)
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    # TODO:
    # photo = models.ImageField()
    description = models.TextField()
    language = models.CharField(max_length=5, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)
    popularity = models.PositiveIntegerField()
    rating = models.FloatField()
    is_public = models.BooleanField(default=False)

class Page(TimestampedModel):
    """
    This class represents a page of a course. All pages belong to some course and have a certain
    index for that particular course. The index determines the order in which the pages have to
    be navigated. There is a flat structure to the pages. This means that a page cannot have sub-pages.
    This was decided because it makes the app more complex while not adding any significant value to the 
    user experience.
    """
    course = models.ForeignKey(Course)
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    popularity = models.PositiveIntegerField() # number of times the page has been viewed
    
    class Meta:
        order_with_respect_to = 'course'

    
    
    
    
    
    
    