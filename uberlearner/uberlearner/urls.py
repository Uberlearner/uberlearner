from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', direct_to_template, {'template': 'under-construction.html'}, 'home'),
    (r'^about/$', direct_to_template, {'template': 'about.html'}, 'about'),
    (r'^contact/$', direct_to_template, {'template': 'under-construction.html'}, 'contact'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
