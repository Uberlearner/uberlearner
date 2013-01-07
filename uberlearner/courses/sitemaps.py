from django.contrib.sitemaps import Sitemap

class CoursesSitemap(Sitemap):
    priority = 0.6

    def items(self):
        from courses.models import Course
        return Course.objects.filter(is_public=True)

    def lastmod(self, course):
        return course.last_modified