from django.db import models

class TimestampedModel(models.Model):
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
