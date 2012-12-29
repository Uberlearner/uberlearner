from django.conf import settings
from storages.backends.s3boto import S3BotoStorage

class S3StaticFileStorage(S3BotoStorage):
    def __init__(self, *args, **kwargs):
        kwargs['bucket'] = getattr(settings, 'STATIC_FILE_BUCKET', getattr(settings, 'AWS_STORAGE_BUCKET_NAME'))
        return super(S3StaticFileStorage, self).__init__(*args, **kwargs)