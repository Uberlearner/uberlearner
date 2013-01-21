from django.db.models import PositiveIntegerField, IntegerField
from django.conf import settings
import djangoratings.fields

SITE_WIDE_AVERAGE_RATING = settings.SITE_WIDE_AVERAGE_RATING

class RatingManager(djangoratings.fields.RatingManager):
    def get_rating(self):
        """
        This method uses the total score from all the votes cast and the number of votes along with
        weighting parameters to determine a rating that isn't massively swayed by individual votes.

        In essence, it uses the average rating on the object_type across the entire site to pretend
        to have "field.weight" number of votes casted with that average score. This makes the outlier
        votes unable to change the total rating much.
        """
        if not (self.votes and self.score):
            return 0
        return (
            float(self.score + (self.field.weight*self.field.get_site_wide_average_rating()))
            / (self.votes + self.field.weight)
        )

class RatingCreator(djangoratings.fields.RatingCreator):
    def __get__(self, instance, type=None):
        if instance is None:
            return self.field
            #raise AttributeError('Can only be accessed via an instance.')
        return RatingManager(instance, self.field)

class RatingField(djangoratings.fields.RatingField):
    """
    An over-ride of djangoratings' rating field.
    https://github.com/dcramer/django-ratings
    """
    def __init__(self, site_wide_average_rating=SITE_WIDE_AVERAGE_RATING, *args, **kwargs):
        super(RatingField, self).__init__(*args, **kwargs)
        self.site_wide_average_rating = site_wide_average_rating
        if not (hasattr(self.site_wide_average_rating, '__call__') or
                isinstance(self.site_wide_average_rating, (int, float, long))):
            raise ValueError('site_wide_average_rating has to be a numeral or a function')

    def get_site_wide_average_rating(self):
        if hasattr(self.site_wide_average_rating, '__call__'):
            return self.site_wide_average_rating()
        elif isinstance(self.site_wide_average_rating, (int, float, long)):
            return self.site_wide_average_rating
        else:
            raise ValueError('site_wide_average_rating has to be a numeral or a function')

    def contribute_to_class(self, cls, name):
        self.name = name

        # Votes tally field
        self.votes_field = PositiveIntegerField(
            editable=False, default=0, blank=True)
        cls.add_to_class("%s_votes" % (self.name,), self.votes_field)

        # Score sum field
        self.score_field = IntegerField(
            editable=False, default=0, blank=True)
        cls.add_to_class("%s_score" % (self.name,), self.score_field)

        self.key = djangoratings.fields.md5_hexdigest(self.name)

        field = RatingCreator(self)

        if not hasattr(cls, '_djangoratings'):
            cls._djangoratings = []
        cls._djangoratings.append(self)

        setattr(cls, name, field)