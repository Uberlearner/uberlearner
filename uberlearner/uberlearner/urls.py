from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from courses.api import CourseResource, UserResource, PageResource
from courses.views import CourseList
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
            'main_js_module': 'uberlearner/js/main/base.js'
        },
        'logged_in_view': CourseList.as_view()
    }, name="home"),
    url(r'^api/', include(v1_api.urls)),
    url(r'^accounts/', include('accounts.urls'), name="accounts"),
    url(r'^courses/', include('courses.urls'), name="courses"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^filestorage/', include('filestorage.urls'), name='filestorage'),
    url(r'^pages', include('django.contrib.flatpages.urls'), name='flatpages'),
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': settings.SITEMAPS}, name='sitemap_index'),
    url(r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': settings.SITEMAPS}),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )