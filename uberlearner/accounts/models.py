from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserProfile(models.Model):
    """
    A model representing the profile of each user.
    """
    # to associate each user with one UserProfile
    user = models.OneToOneField(User)

    # Other fields here
    first_name = models.CharField(max_length=30, blank=True)
    middle_name = models.CharField(max_length=60, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    dob = models.DateField(null=True)

    def __unicode__(self):
        return self.user.username

def create_user_profile(sender, instance, created, **kwargs):
    """
    When a new user is created, a profile needs to be associated with
    that user. This method is used to do so by attaching it as a 
    listener to the post_save signal for the User model.
    """
    if created:
        UserProfile.objects.create(user=instance)

# Make sure that a new profile is created when a new user is
# created using the create_user_profile function.
post_save.connect(create_user_profile, sender=User)

