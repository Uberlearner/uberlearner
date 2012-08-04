from django.db import models
from courses.widgets.models import CourseWidget

class Text(CourseWidget):
    """
    A text widget just represents a text block in a course page.
    """
    text = models.TextField()
