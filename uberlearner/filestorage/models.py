from easy_thumbnails.files import get_thumbnailer
import os
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField
from storages.backends.s3boto import S3BotoStorage

def uberphoto_image_path_generator(instance=None, filename=None):
    """
    This method generates the filepath for each photo when it is about to be stored. Currently the path takes
    the format:
    <username>/images/<imagename>.

    This also means that the thumbnails will automatically get stored at:
    <username>/images/thumbnails/<imagename>_<thumbnails_params>.jpg
    """
    if not filename:
        #the file already exists in the database
        filename = instance.photo.name
    path = os.path.join(instance.user.username, 'images', filename)
    return path

class UberPhoto(models.Model):
    """
    Represents all the images that the users have uploaded. Each image has to have an user field that indicates
    the owner of the image.
    """
    user = models.ForeignKey(User, related_name='user_images')
    image = ThumbnailerImageField(
        upload_to=uberphoto_image_path_generator,
        storage=S3BotoStorage(
            location='development/filestorage' if settings.DEBUG else 'filestorage'
        ),
        thumbnail_storage=S3BotoStorage(
            location='development/filestorage' if settings.DEBUG else 'filestorage',
            reduced_redundancy=True #saves money on S3!
        )
    )

    def get_url_dict(self):
        """
        Returns a dictionary of the form:
        {
            'thumbnail': <thumbnail_url>,
            'original': <original_full_sized_image_url>
        }
        """
        thumbnail = get_thumbnailer(self.image)['thumbnail']
        return {
            'thumbnail': thumbnail.url,
            'original': self.image.url
        }
