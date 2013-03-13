import os
import urlparse
from django.conf import settings
from storages.backends.s3boto import S3BotoStorage
from django.core.files import storage as django_storage

class S3StaticFileStorage(S3BotoStorage):
    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = getattr(settings, 'STATIC_FILE_BUCKET', getattr(settings, 'AWS_STORAGE_BUCKET_NAME'))
        super(S3StaticFileStorage, self).__init__(*args, **kwargs)


class FileSystemStorage(django_storage.FileSystemStorage):
    """
    To be independent of the file system storages, we will be using the default_storage declared in the settings files.
    This storage will be the new default storage unless the user over-rides this setting. This means that this storage
    must be able to ignore additional parameters thrown at it because they may be aimed at other storages (which can be
    used by changing the required settings).

    To see this in action, see the photo attribute of the Course model in the courses application.
    """
    def __init__(self, **kwargs):
        location = kwargs.get('location', settings.MEDIA_ROOT)
        base_url = kwargs.get('base_url', settings.MEDIA_URL)

        # if this storage is being used, then the entire path needs to be in the location variable
        if not location.startswith(settings.MEDIA_ROOT):
            full_location = os.path.join(settings.MEDIA_ROOT, location)
        else:
            full_location = location
            location = full_location[len(settings.MEDIA_ROOT):]
            if location.startswith('/'):
                location = location[1:]

        if not base_url.endswith(location):
            base_url = urlparse.urljoin(base_url, location)
        if not base_url[-1] == '/':
            base_url += '/'

        super(FileSystemStorage, self).__init__(location=full_location, base_url=base_url)