from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', direct_to_template, {'template': 'under-construction.html'}, 'home'),
    (r'^about/$', direct_to_template, {'template': 'about.html'}, 'about'),
    (r'^contact/$', direct_to_template, {'template': 'under-construction.html'}, 'contact'),
    url(r'^accounts/', include('accounts.urls'), name="accounts"),
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )