from django import forms
from django.forms import models
from courses.models import Course

class CourseForm(models.ModelForm):
    class Meta:
        model = Course
        exclude = ('instructor', )