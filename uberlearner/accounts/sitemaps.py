from django.contrib.sitemaps import Sitemap

class AccountsSitemap(Sitemap):
    priority = 0.4

    def items(self):
        from accounts.models import UserProfile
        return UserProfile.objects.all()