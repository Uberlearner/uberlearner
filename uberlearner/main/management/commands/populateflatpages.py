from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.management import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (

    )
    help = 'Adds in flatpage data into the database from the flatpages settings file'

    def handle(self, *args, **options):
        config = settings.FLATPAGE_CONFIG

        FlatPage.objects.all().delete()

        for url_data in config.itervalues():
            flatpage = FlatPage.objects.create(**url_data)
            flatpage.sites.add(Site.objects.get(pk=1))