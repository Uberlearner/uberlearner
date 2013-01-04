from django.contrib import admin
from courses.models import Course, Instructor, Page, Enrollment

class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'language', 'popularity', 'is_public', 'deleted']
    prepopulated_fields = {
        'slug': ('title', )
    }
    def queryset(self, request):
        qs = self.model.all_objects.get_query_set()

        # the following is needed from the superclass
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

class InstructorAdmin(admin.ModelAdmin):
    list_display = ['user', 'popularity']
    
class PageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Course, CourseAdmin)
admin.site.register(Instructor, InstructorAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Enrollment)
