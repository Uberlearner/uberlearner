from courses.sitemaps import CoursesSitemap
from accounts.sitemaps import AccountsSitemap
from django.contrib.sitemaps import FlatPageSitemap

SITEMAPS = {
    'courses': CoursesSitemap,
    'accounts': AccountsSitemap,
    'flatpages': FlatPageSitemap
}
