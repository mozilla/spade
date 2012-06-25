import os

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from spade.model.models import CrawlList

class Command(BaseCommand):
    help = "Manage sites to crawl."

    option_list = BaseCommand.option_list + (
        make_option('--add',
                    action='store',
                    dest='add',
                    default=False,
                    help='Add new site to crawl'),
        make_option('--list',
                    action='store_true',
                    dest='list',
                    default=False,
                    help='List sites we currently crawl'),
        make_option('--remove',
                    action='store',
                    dest='remove',
                    default=False,
                    help='Remove url from crawl database')
        )

    def handle(self, *args, **options):

        new = options.get('add')
        remove = options.get('remove')

        if options.get('list'):
            self.stdout.write("Listing all urls we currently crawl:\n")
            self.stdout.write("=====================================\n")

            for listitem in CrawlList.objects.all():
                self.stdout.write(listitem.url+'\n')

        elif new:
            new_url = CrawlList()
            new_url.url = str(new)
            new_url.save()
            self.stdout.write('Successfully inserted "%s"\n' % str(new))

        elif remove:
            try:
                url_to_remove = CrawlList.objects.get(url=remove)
            except CrawlList.DoesNotExist:
                raise CommandError("No such url exists. We dont crawl that.")

            url_to_remove.delete()
            self.stdout.write('Successfully removed "%s"\n' % str(remove))
        else:
            raise CommandError("You must give a valid parameter.")
