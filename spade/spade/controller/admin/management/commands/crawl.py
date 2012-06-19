from django.core.management.base import BaseCommand, CommandError
from optparse import make_option


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--someflag',
            action='store_true',
            dest='someflag',
            default=False,
            help='Sample help for this flag'),
        )

    # Put crawler here
    def handle(self, *args, **options):
        print "Hello!"

        if options['someflag']:
            print "Do something here"
