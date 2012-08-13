from django.views.generic.edit import CreateView, UpdateView
from courses.models import Course
from courses.forms import CourseForm
from django.views.generic.detail import DetailView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic.base import View
from django.core.urlresolvers import reverse
from django.http import Http404

class CourseCreate(CreateView):
    model = Course
    form_class = CourseForm
    
    def form_valid(self, form):
        form.instance.instructor = self.request.user
        return super(CourseCreate, self).form_valid(form)
    
    def get_success_url(self):
        return reverse('course.manage', kwargs={'username': self.request.user.username, 'slug': self.object.slug})
    
class CourseView(DetailView):
    model = Course
    object_name = 'course'
    
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
                instructor=self.kwargs['username'],
            ))
        if instructor != self.request.user and not course.is_public:
            raise Http404("{course} by {instructor} is not ready for public viewing".format(
                course=self.kwargs[self.slug_url_kwarg],
                instructor=self.kwargs['username'],
            ))
        return course
    
class CourseEdit(UpdateView):
    model = Course
    form_class = CourseForm
    
    def get_queryset(self):
        instructor = get_object_or_404(User, username=self.kwargs['username'])
        return Course.objects.get(slug=self.kwargs[self.slug_url_kwarg], instructor=instructor)
    
class CourseManage(View):
    model = Course