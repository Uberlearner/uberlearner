from django.contrib import admin
from courses.models import Course, Instructor, Page

class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'language', 'popularity', 'is_public']
    prepopulated_fields = {
        'slug': ('title', )
    }

class InstructorAdmin(admin.ModelAdmin):
    list_display = ['user', 'popularity']
    
class PageAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title', )
    }

admin.site.register(Course, CourseAdmin)
admin.site.register(Instructor, InstructorAdmin)
admin.site.register(Page, PageAdmin)
