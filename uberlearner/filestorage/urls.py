from django.conf.urls import patterns, url
from filestorage.views import Browse

urlpatterns = patterns('',
    url(r'^browse/$', Browse.as_view(), name='filestorage.browse'),
)
