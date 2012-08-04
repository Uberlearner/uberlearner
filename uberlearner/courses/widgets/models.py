from main.models import TimestampedModel
from django.db import models
from courses.models import Page

class CourseWidget(TimestampedModel):
    """
    Every page in a course is composed of many widgets. These can be of types such as text, video, quiz etc.
    They have a position in the page.
    
    TODO: figure out whether this is needed at all. Maybe tinyMCE or another editor could support custom plugins 
    that would do the job of these widgets.
    """
    page = models.ForeignKey(Page)
    
    class Meta:
        order_with_respect_to = 'page'
        abstract = True
