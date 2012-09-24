from django.core.exceptions import PermissionDenied
from django.views.generic.edit import CreateView, UpdateView, FormView
from courses.models import Course
from courses.forms import CourseForm, CoursePageForm
from django.views.generic.detail import DetailView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic.base import View, TemplateView
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.views.generic.list import ListView

class CourseCreate(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/create/index.html'
    
    def form_valid(self, form):
        form.instance.instructor = self.request.user
        return super(CourseCreate, self).form_valid(form)
    
    def get_success_url(self):
        return reverse('course.edit', kwargs={'username': self.object.instructor.username, 'slug': self.object.slug})
    
class CourseView(DetailView):
    model = Course
    object_name = 'course'
    template_name = 'courses/read/detail/index.html'
    
    def get_object(self, queryset=None):
        instructor = get_object_or_404(User, username=self.kwargs['username'])
        try:
            if queryset is None:
                course = Course.objects.get(slug=self.kwargs[self.slug_url_kwarg], instructor=instructor)
            else:
                course = queryset.get(slug=self.kwargs[self.slug_url_kwarg], instructor=instructor)
        except Course.DoesNotExist:
            raise Http404("{course} by {instructor} could not be found!".format(
                course=self.kwargs[self.slug_url_kwarg],
                instructor=self.kwargs['username']
            ))
        if instructor != self.request.user and not course.is_public:
            raise PermissionDenied("{course} by {instructor} is not ready for public viewing".format(
                course=self.kwargs[self.slug_url_kwarg],
                instructor=self.kwargs['username']
            ))
        return course
    
class CourseEdit(UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/update/edit/index.html'

    def get_object(self, queryset=None):
        instructor = get_object_or_404(User, username=self.kwargs['username'])
        try:
            if queryset is None:
                course = Course.objects.get(slug=self.kwargs[self.slug_url_kwarg], instructor=instructor)
            else:
                course = queryset.get(slug=self.kwargs[self.slug_url_kwarg], instructor=instructor)
        except Course.DoesNotExist:
            raise Http404("{course} by {instructor} could not be found!".format(
                course=self.kwargs[self.slug_url_kwarg],
                instructor=self.kwargs['username']
            ))
        # nobody except the instructor can edit a course
        if instructor != self.request.user:
            raise PermissionDenied("You do not have the permissions to edit {course} by {instructor}".format(
                course=self.kwargs[self.slug_url_kwarg],
                instructor=self.kwargs['username']
            ))
        return course
    
class CourseManage(CourseView):
    template_name = 'courses/update/manage/index.html'

    def get_object(self, queryset=None):
        course = super(CourseManage, self).get_object(queryset)
        # nobody except the instructor can manage a course
        if course.instructor != self.request.user:
            raise PermissionDenied("Your do not have the permissions to manage {course} by {instructor}".format(
                course=course,
                instructor=self.kwargs['username']
            ))

        return course

    def get_context_data(self, **kwargs):
        context_data = super(CourseManage, self).get_context_data(**kwargs)
        context_data['main_js_module'] = 'uberlearner/js/courses/manage/main.js'
        return context_data
    
class CourseList(TemplateView):
    """
    This view shows a list of all the courses available.
    """
    template_name = 'courses/read/list/public/index.html'
    
    def get_context_data(self, **kwargs):
        context_data = super(CourseList, self).get_context_data(**kwargs)
        context_data['main_js_module'] = 'uberlearner/js/courses/course-list.js'
        return context_data
    
class UserCourses(TemplateView):
    """
    This view shows a list of all the courses that the current user has authored.
    TODO
    """
    template_name = 'courses/read/list/instructor/index.html'
    
    def get_context_data(self, **kwargs):
        context_data = super(UserCourses, self).get_context_data(**kwargs)
        context_data['instructor'] = User.objects.get(username=kwargs['username'])
        context_data['main_js_module'] = 'uberlearner/js/courses/instructor-course-list.js'
        return context_data