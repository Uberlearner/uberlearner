from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', direct_to_template, {'template': 'under-construction.html'}, 'home'),
    (r'^about/$', direct_to_template, {'template': 'about.html'}, 'about'),
    (r'^contact/$', direct_to_template, {'template': 'under-construction.html'}, 'contact'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
