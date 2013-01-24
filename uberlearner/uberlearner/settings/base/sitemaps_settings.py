# Because of the way django evaluates the settings file, importing the Sitemap classes
# at start-up time (when the settings file is parsed) leads to an invalid setting being
# read somewhere in the libraries backing up the Sitemap classes.
# This means that the import of these sitemaps must not be done and startup-time.
#
# The good thing about how the sitemaps are evaluated on receiving a sitemap request is that if
# the sitemap objects are callables, then they are called first. This means we can envelope these
# imports using callables.

def envelope_sitemap(sitemap_class_path):
    path_components = sitemap_class_path.rsplit('.', 1)
    def sitemap_envelope(*args, **kwargs):
    # dynamically import the sitemap
        module = __import__(path_components[0], fromlist=path_components[-1:])
        klass = getattr(module, path_components[-1])
        # make an instance of the sitemap class obtained and return it
        return klass(*args, **kwargs)
    return sitemap_envelope

SITEMAPS = {
    'courses': envelope_sitemap('courses.sitemaps.CoursesSitemap'),
    'accounts': envelope_sitemap('accounts.sitemaps.AccountsSitemap'),
    'flatpages': envelope_sitemap('django.contrib.sitemaps.FlatPageSitemap'),
}
