from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from courses.api import CourseResource, UserResource, PageResource
from tastypie.api import Api
from accounts import views as accounts_views

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(CourseResource())
v1_api.register(UserResource())
v1_api.register(PageResource())

urlpatterns = patterns('',
    url(r"^$", accounts_views.login, {
        'template_name': 'index.html',
        'verification_sent_template': 'allauth/account/verification_sent.html',
        'extra_context': {
            'main_js_module': 'uberlearner/js/main/under-construction.js'
        }
    }, name="home"),
    url(r'^api/', include(v1_api.urls)),
    url(r'^accounts/', include('accounts.urls'), name="accounts"),
    url(r'^courses/', include('courses.urls'), name="courses"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^filestorage/', include('filestorage.urls'), name='filestorage'),
    url(r'^pages/', include('flatpages.urls'), name='flatpages'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )