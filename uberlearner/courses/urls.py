from django.conf.urls import patterns, url
from django.views.generic.simple import direct_to_template
from courses.views import CourseCreate, CourseView, CourseSettings, CourseManage, UserCourses, CourseList, CoursePage
from courses import JS_BASE_DIR_COURSE
import os

urlpatterns = patterns('',
    url(r'^$',
        direct_to_template, {
            'template': 'courses/course/read/list/public/isotope.html',
            'extra_context': {
                'main_js_module': os.path.join(JS_BASE_DIR_COURSE, 'list', 'public.js'),
            }
        },
        'course.list'
    ),
    url(r'^create/$', CourseCreate.as_view(), name='course.create'),

    url(r'^(?P<username>[0-9a-zA-Z@.+_-]+)/$', UserCourses.as_view(), name='course.by_user'),
    url(r'^(?P<username>[0-9a-zA-Z@.+_-]+)/(?P<slug>[0-9a-zA-Z-]+)$', CourseView.as_view(), name='course.view'),
    url(r'^(?P<username>[0-9a-zA-Z@.+_-]+)/(?P<slug>[0-9a-zA-Z-]+)/settings$', CourseSettings.as_view(), name='course.settings'),
    url(r'^(?P<username>[0-9a-zA-Z@.+_-]+)/(?P<slug>[0-9a-zA-Z-]+)/manage$', CourseManage.as_view(), name='course.manage'),

    url(r'^(?P<username>[0-9a-zA-Z@.+_-]+)/(?P<slug>[0-9a-zA-Z-]+)/pages$', CoursePage.as_view(), name='page.first.view'),
    url(r'^(?P<username>[0-9a-zA-Z@.+_-]+)/(?P<slug>[0-9a-zA-Z-]+)/pages/(?P<pk>\d+)$', CoursePage.as_view(), name='page.view'),
) 
