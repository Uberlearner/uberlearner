from django.db import models
from easy_thumbnails.signals import saved_file
from easy_thumbnails.signal_handlers import generate_aliases_global

class TimestampedModel(models.Model):
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

#to pre-generate the thumbnails globally
saved_file.connect(generate_aliases_global, dispatch_uid='pre-generation-of-thumbnails')