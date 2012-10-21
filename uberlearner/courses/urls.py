from django.conf.urls import patterns, url
from courses.views import CourseCreate, CourseView, CourseEdit, CourseManage, UserCourses, CourseList, CoursePage

urlpatterns = patterns('',
    url(r'^$', CourseList.as_view(), name='course.list'),
    url(r'^create/$', CourseCreate.as_view(), name='course.create'),

    url(r'^(?P<username>[0-9a-zA-Z@.+_-]+)/$', UserCourses.as_view(), name='course.by_user'),
    url(r'^(?P<username>[0-9a-zA-Z@.+_-]+)/(?P<slug>[0-9a-zA-Z-]+)$', CourseView.as_view(), name='course.view'),
    url(r'^(?P<username>[0-9a-zA-Z@.+_-]+)/(?P<slug>[0-9a-zA-Z-]+)/edit$', CourseEdit.as_view(), name='course.edit'),
    url(r'^(?P<username>[0-9a-zA-Z@.+_-]+)/(?P<slug>[0-9a-zA-Z-]+)/manage$', CourseManage.as_view(), name='course.manage'),

    url(r'^(?P<username>[0-9a-zA-Z@.+_-]+)/(?P<slug>[0-9a-zA-Z-]+)/pages$', CoursePage.as_view(), name='page.first.view'),
    url(r'^(?P<username>[0-9a-zA-Z@.+_-]+)/(?P<slug>[0-9a-zA-Z-]+)/pages/(?P<pk>\d+)$', CoursePage.as_view(), name='page.view'),
) 
