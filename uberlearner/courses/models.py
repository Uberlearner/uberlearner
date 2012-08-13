from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from main.models import TimestampedModel
from django.db.models.signals import post_save
################################
# Main models
################################
        
class Instructor(models.Model):
    """
    This model encapsulates the various properties of a user who has signed
    on to be an instructor.
    """
    user = models.OneToOneField(User, related_name="instructor_profile")
    #rating = models.FloatField(default=0, editable=False)
    popularity = models.PositiveIntegerField(default=0, editable=False) # number of times their course has been used
    
    def __unicode__(self):
        return self.user.__unicode__()
    
    @classmethod
    def make_user_instructor(cls, sender, instance, created, **kwargs):
        """
        When a new user is created, an instructor profile is associated with 
        that user. This is the method that does it after receiving a post_save
        signal from the User model.
        """
        if created:
            cls.objects.create(user=instance)
    
class Course(TimestampedModel):
    """
    This model encapsulates the various parameters of a course.
    """
    instructor = models.ForeignKey(User)
    # TEACHING ASSISTANTS AND TRANSLATORS WILL BE IMPLEMENTED LATER
    # teaching_assistants = models.ManyToManyField(Instructor)
    # translators = models.ManyToManyField(Translator)
    title = models.CharField(max_length=50, help_text="A slug is a URL friendly name \
        containing only letters, numbers, underscores or hyphens.")
    slug = models.SlugField(max_length=50)
    # TODO:
    # photo = models.ImageField()
    description = models.TextField(blank=True)
    language = models.CharField(max_length=5, choices=settings.LANGUAGES, default='en')
    popularity = models.PositiveIntegerField(default=0, editable=False) # number of times the course has been enrolled in
    #rating = models.FloatField(default=0, editable=False)
    is_public = models.BooleanField(default=False, help_text="If checked, it will enable anyone to see your course.")
    
    class Meta:
        unique_together = (('slug', 'instructor'), )
    
    def __unicode__(self):
        return self.title

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
    popularity = models.PositiveIntegerField(default=0, editable=False) # number of times the page has been viewed
    
    class Meta:
        order_with_respect_to = 'course'
        
    def __unicode__(self):
        return self.title

post_save.connect(Instructor.make_user_instructor, sender=User)
    
    
    
    
    
    