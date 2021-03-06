from django.core.exceptions import ValidationError
from django.core.files.storage import get_storage_class
from django.db.models import F, Sum
from easy_thumbnails.fields import ThumbnailerImageField
import os
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.template.defaultfilters import slugify
from main.models import TimestampedModel
from django.db.models.signals import post_save
from ratings.fields import RatingField

default_storage_class = get_storage_class()

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
    
    @models.permalink
    def get_absolute_url(self):
        return ('course.by_user', (), {
            'username': self.user.username,
        })
    
    @classmethod
    def make_user_instructor(cls, sender, instance, created, **kwargs):
        """
        When a new user is created, an instructor profile is associated with 
        that user. This is the method that does it after receiving a post_save
        signal from the User model.
        """
        if created:
            cls.objects.create(user=instance)

class Enrollment(models.Model):
    student = models.ForeignKey(User, related_name='enrollments')
    course = models.ForeignKey('Course', related_name='enrollments')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "{student} - {course} - {timestamp}".format(
            student=str(self.student),
            course=str(self.course),
            timestamp=str(self.timestamp)
        )

    @classmethod
    def increment_course_popularity(cls, sender, instance, created, **kwargs):
        """
        When an enrollment instance is saved, this method is called through the post_save signal. This method
        has to check whether this was indeed the creation of a new instance (modifications of enrollment records
        should not happen anyways). If this was indeed the creation of a new instance, the popularity of the course
        has to be incremented.
        """
        if created:
            instance.course.popularity = F('popularity') + 1  # increment course popularity
            instance.course.save()


def course_image_path(instance=None, filename=None):
    """
    This method is used to generate the path for the course image by the model.
    """
    if not filename:
        #the file already exists in the database
        filename = instance.photo.name
    path = os.path.join(instance.instructor.username, filename)
    return path


class NonDeletedCoursesManager(models.Manager):
    def get_query_set(self):
        return super(NonDeletedCoursesManager, self).get_query_set().filter(deleted=False)


class Course(TimestampedModel):
    """
    This model encapsulates the various parameters of a course.
    """
    #model fields
    instructor = models.ForeignKey(User, related_name='instructor_courses')
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, help_text="A slug is a URL friendly name \
        containing only letters, numbers, underscores or hyphens.")
    # TODO:
    photo = ThumbnailerImageField(
        upload_to=course_image_path,
        storage=default_storage_class(
            location='courses',
            querystring_auth=False
        ),
        thumbnail_storage=default_storage_class(
            location='courses',
            reduced_redundancy=True,  # this saves money!
            querystring_auth=False
        ),
        default='defaultCourseImage.png',
        blank=True
    )
    description = models.TextField(blank=True)

    language = models.CharField(max_length=5, choices=settings.LANGUAGES, default='en')
    popularity = models.PositiveIntegerField(default=0, editable=False)  # number of times the course has been enrolled in
    rating = RatingField(range=settings.COURSE_RATING_RANGE, can_change_vote=True, allow_delete=False,
        allow_anonymous=False, use_cookies=False, weight=settings.COURSE_RATING_WEIGHT)
    is_public = models.BooleanField(
        default=False,
        help_text="If checked, everybody will be able to see your course. Click this when your course is ready for public consumption",
        verbose_name="Is published"
    )
    students = models.ManyToManyField(User, through=Enrollment, blank=True, null=True, related_name='enrolled_courses')
    # a boolean used to mark courses deleted without actually deleting them
    deleted = models.BooleanField(default=False, help_text="Marks a course as deleted.")

    refresh_slug = False # a boolean indicating whether the save method should re-create the slug
    objects = NonDeletedCoursesManager()
    all_objects = models.Manager()
    
    class Meta:
        unique_together = (('slug', 'instructor'), )
    
    def __unicode__(self):
        return self.title
    
    @models.permalink
    def get_absolute_url(self):
        return ('course.view', (), {
            'username': self.instructor.username,
            'slug': self.slug
        })

    @models.permalink
    def get_resource_uri(self, url_name='api_dispatch_detail'):
        # avoid circular import
        from courses.api import CourseResource
        from uberlearner.urls import v1_api

        return (url_name, (), {
            'resource_name': CourseResource._meta.resource_name,
            'api_name': v1_api.api_name,
            'pk': self.id
        })

    def get_enrollment_resource_uri(self):
        return self.get_resource_uri(url_name='api_course_enroll')

    def get_rating_resource_uri(self):
        return self.get_resource_uri(url_name='api_course_rate')

    def is_enrolled(self, user):
        return self.enrollments.filter(student=user).exists()

    @property
    def estimated_effort(self):
        return self.pages.aggregate(Sum('estimated_effort'))['estimated_effort__sum']

    def clean(self):
        """
        This is the method that gets called by Django for the validation of the model as a whole:
        (https://docs.djangoproject.com/en/dev/ref/models/instances/?from=olddocs#validating-objects).

        This method checks for the following:
        1) A model cannot be marked "deleted" if someone is already enrolled in the course.
        2) A model cannot be marked "private" if someone is already enrolled in the course.
        """
        if self.deleted and self.enrollments.exists():
            raise ValidationError("A course with active enrollments cannot be deleted")
        if not self.is_public and self.enrollments.exists():
            raise ValidationError("A course with active enrollments cannot be made private")

    def save(self, force_insert=False, force_update=False, using=None):
        """
        The slug field for the course model is supposed to be auto-generated. Django doesn't provide this
        functionality. So this over-ride of save does that.

        This method borrows heavily from: http://djangosnippets.org/snippets/512/
        """
        if not self.slug or self.refresh_slug:
            slug = slugify(self.title)
            all_slugs = [sl.values()[0] for sl in Course.objects.filter(instructor=self.instructor).values('slug')]
            if slug in all_slugs:
                import re
                counter_finder = re.compile(r'-\d+$')
                counter = 2
                slug = "{0}-{1}".format(slug, counter)
                while slug in all_slugs:
                    slug = re.sub(counter_finder, "-{0}".format(counter), slug)
                    counter += 1
            self.slug = slug
            self.refresh_slug = False
        return super(Course, self).save(force_insert, force_update, using)

    def delete(self, using=None, real_delete=False):
        """
        For deletion, the courses will be merely marked as deleted. If the actual data has to be deleted, then the real_delete
        parameter will have to be true.
        """
        if not real_delete:
            self.deleted = True
            self.clean()
            self.save()
        else:
            return super(Course, self).delete(using=using)

class Page(TimestampedModel):
    """
    This class represents a page of a course. All pages belong to some course and have a certain
    index for that particular course. The index determines the order in which the pages have to
    be navigated. There is a flat structure to the pages. This means that a page cannot have sub-pages.
    This was decided because it makes the app more complex while not adding any significant value to the 
    user experience.
    """
    course = models.ForeignKey(Course, related_name='pages')
    title = models.CharField(max_length=50, help_text="50 characters max")
    summary = models.CharField(max_length=300, help_text="300 characters max", null=True, blank=True)
    estimated_effort = models.PositiveIntegerField(
        help_text="Estimated study-time for this page (in minutes)",
        null=True, blank=True
    )
    popularity = models.PositiveIntegerField(default=0, editable=False) # number of times the page has been viewed
    html = models.TextField()
    
    class Meta:
        order_with_respect_to = 'course'
        
    def __unicode__(self):
        return self.title

    @models.permalink
    def get_resource_uri(self, url_name='api_dispatch_detail'):
        # avoid circular import
        from courses.api import PageResource
        from uberlearner.urls import v1_api

        return (url_name, (), {
            'resource_name': PageResource._meta.resource_name,
            'api_name': v1_api.api_name,
            'pk': self.id
        })

post_save.connect(Instructor.make_user_instructor, sender=User)
post_save.connect(Enrollment.increment_course_popularity, sender=Enrollment)