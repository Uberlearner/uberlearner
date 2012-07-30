from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse

class UserProfile(models.Model):
    """
    A model representing the profile of each user.
    """
    # to associate each user with one UserProfile
    user = models.OneToOneField(User, related_name="profile")

    # Other fields here
    dob = models.DateField(null=True, blank=True)
    summary = models.TextField(blank=True)

    def __unicode__(self):
        return self.user.username
    
    def get_absolute_url(self):
        return reverse('account_user_profile_with_username', kwargs={'username': self.user.username})

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

