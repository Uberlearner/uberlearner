from django.db import models
from courses.uberwidgets.models import UberWidget

class Text(UberWidget):
    """
    A text widget just represents a text block in a course page.
    """
    text = models.TextField()
