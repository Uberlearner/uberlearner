from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.conf import settings
from django.contrib import admin
from courses.api import CourseResource, UserResource, PageResource
from tastypie.api import Api
admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(CourseResource())
v1_api.register(UserResource())
v1_api.register(PageResource())

urlpatterns = patterns('',
    (r'^$', direct_to_template, {'template': 'under-construction.html'}, 'home'),
    (r'^api/', include(v1_api.urls)),
    (r'^about/$', direct_to_template, {'template': 'about.html'}, 'about'),
    (r'^contact/$', direct_to_template, {'template': 'under-construction.html'}, 'contact'),
    url(r'^accounts/', include('accounts.urls'), name="accounts"),
    url(r'^courses/', include('courses.urls'), name="courses"),
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )