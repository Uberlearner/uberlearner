from django.conf.urls.defaults import patterns, url
from courses.views import CourseCreate, CourseView, CourseEdit, CourseManage, UserCourses, CourseList

urlpatterns = patterns('',
    url(r'^create/$', CourseCreate.as_view(), name='course.create'),
    url(r'^$', CourseList.as_view(), name='course.list'),
    url(r'^(?P<username>[0-9a-zA-Z@.+_-]+)/$', UserCourses.as_view(), name='course.user_list'),
    url(r'^(?P<username>[0-9a-zA-Z@.+_-]+)/(?P<slug>[0-9a-zA-Z-]+)$', CourseView.as_view(), name='course.view'),
    url(r'^(?P<username>[0-9a-zA-Z@.+_-]+)/(?P<slug>[0-9a-zA-Z-]+)/edit$', CourseEdit.as_view(), name='course.edit'),
    url(r'^(?P<username>[0-9a-zA-Z@.+_-]+)/(?P<slug>[0-9a-zA-Z-]+)/manage$', CourseManage.as_view(), name='course.manage'),
) 
