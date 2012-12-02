from django.conf.urls import patterns, url
from filestorage.views import Browse, upload

urlpatterns = patterns('',
    url(r'^browse/$', Browse.as_view(), name='filestorage.browse'),
    url(r'^upload/$', upload, name='filestorage.upload'),
)
