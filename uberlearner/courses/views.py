from django.contrib import messages
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.views.generic.edit import CreateView, UpdateView, FormView, DeletionMixin
from courses.models import Course, Page
from courses.forms import CourseForm, CoursePageForm
from django.views.generic.detail import DetailView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import View, TemplateView
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
import os
from courses import JS_BASE_DIR, JS_BASE_DIR_COURSE, JS_BASE_DIR_PAGE

class CourseCreate(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course/create/index.html'

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        messages.add_message(self.request, messages.SUCCESS, 'Your course has been successfully created!')
        return super(CourseCreate, self).form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, 'Your course could not be created')
        return super(CourseCreate, self).form_invalid(form)

    def get_success_url(self):
        return reverse('course.view', kwargs={'username': self.object.instructor.username, 'slug': self.object.slug})

class CourseView(DetailView):
    """
    This view is the one that the user sees on clicking the course link. It gives the user an overview
    of the course along with the option to enroll. In addition, it lets the instructor of the course get
    into the edit/manage modes.
    """
    model = Course
    object_name = 'course'
    template_name = 'courses/course/read/detail/index.html'

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

    def get_context_data(self, **kwargs):
        context_data = super(CourseView, self).get_context_data(**kwargs)
        # by this point course must have been added to the context_data and can be used to get the enrollment object
        try:
            if self.request.user.is_authenticated():
                enrollment = context_data['course'].enrollments.filter(student=self.request.user).get()
            else:
                enrollment = None
        except ObjectDoesNotExist:
            enrollment = None
        context_data['enrollment'] = enrollment
        context_data['all_enrollments'] = context_data['course'].enrollments.all()
        context_data['main_js_module'] = os.path.join(JS_BASE_DIR_COURSE, 'detail', 'main.js')
        return context_data

class CoursePage(CourseView):
    """
    This is the view the user sees when he/she is enrolled in the course. It contains all the pages in the course
    along with a auto-hidden TOC. This is also the view that will contain the quizes etc.
    """
    model = Page
    object_name = 'page'
    template_name = 'courses/page/read/detail/index.html'

    def get_object(self, queryset=None):
        """
        It is possible for this view to be triggered by a url that doesn't provide a page id. In that case, we try
        to get the first page of the course. If the course doesn't contain a page, then we just return None
        """
        self.course = super(CoursePage, self).get_object(queryset=queryset)
        # if the course has been successfully acquired, then it must mean that the user has the rights to view that
        # course. Hence, no authorization checks have to be made regarding the page.
        if not 'pk' in self.kwargs:
            try:
                page = self.course.pages.all()[0]
            except IndexError:
                page = None
        else:
            page = get_object_or_404(Page, course=self.course, pk=self.kwargs['pk'])
        return page

    def get_context_data(self, **kwargs):
        context_data = super(CourseView, self).get_context_data(**kwargs) #get the original context data from DetailView not CourseView
        context_data['main_js_module'] = os.path.join(JS_BASE_DIR_PAGE, 'list', 'main.js')
        context_data['course'] = self.course #we do this because the page variable might be None and the course will not be accessible
        return context_data
    
class CourseSettings(UpdateView):
    """
    This is the view that the instructor uses to edit the basic properties of the course. These include course title,
    description, visibility etc.
    """
    model = Course
    form_class = CourseForm
    template_name = 'courses/course/update/settings/index.html'

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

    def get_context_data(self, **kwargs):
        context_data = super(CourseSettings, self).get_context_data(**kwargs)
        context_data['main_js_module'] = 'uberlearner/js/main/base.js'
        return context_data

    def post(self, request, *args, **kwargs):
        course = self.get_object()
        if 'deleted' in request.POST and request.POST['deleted'] == 'on':
            course.delete()
            return redirect('course.by_user', username=request.user.username)
        else:
            return super(CourseSettings, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Successfully updated the course settings')
        return super(CourseSettings, self).form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, 'Could not update course settings')
        return super(CourseSettings, self).form_invalid(form)
    
class CourseManage(CourseView):
    template_name = 'courses/course/update/manage/index.html'

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
        context_data['main_js_module'] = os.path.join(JS_BASE_DIR_COURSE, 'manage', 'main.js')
        return context_data
    
class CourseList(TemplateView):
    """
    This view shows a list of all the courses available.
    """
    template_name = 'courses/course/read/list/public/isotope.html'
    
    def get_context_data(self, **kwargs):
        context_data = super(CourseList, self).get_context_data(**kwargs)
        context_data['main_js_module'] = os.path.join(JS_BASE_DIR_COURSE, 'list', 'public.js')
        return context_data
    
class UserCourses(TemplateView):
    """
    This view shows a list of all the courses that the current user has authored.
    TODO
    """
    template_name = 'courses/course/read/list/instructor/index.html'
    
    def get_context_data(self, **kwargs):
        context_data = super(UserCourses, self).get_context_data(**kwargs)
        context_data['instructor'] = User.objects.get(username=kwargs['username'])
        context_data['main_js_module'] = os.path.join(JS_BASE_DIR_COURSE, 'instructor-course-list.js')
        return context_data