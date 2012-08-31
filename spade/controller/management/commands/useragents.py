from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from spade.model.models import UserAgent


class Command(BaseCommand):
    help = "Manage user agents to use in each crawl."

    option_list = BaseCommand.option_list + (
        make_option('--add',
                    action='store',
                    dest='add',
                    default=False,
                    help='Add new useragent string to include'),
        make_option('--list',
                    action='store_true',
                    dest='list',
                    default=False,
                    help='List currently indexed useragent strings'),
        make_option('--remove',
                    action='store',
                    dest='remove',
                    default=False,
                    help='Remove useragent string from database'),
        make_option('--primary',
                    action='store_true',
                    dest='primary',
                    default=False,
                    help='Added user-agent will be primary mobile UA'),
        )

    def handle(self, *args, **options):

        new = options.get('add')
        remove = options.get('remove')

        if options.get('list'):
            self.stdout.write("Listing all saved user agent strings:\n")
            self.stdout.write("=====================================\n")

            for agent in UserAgent.objects.all():
                self.stdout.write(agent.ua_string + '\n')

        elif new:
            new_ua = UserAgent()
            new_ua.ua_string = str(new)
            new_ua.save()
            self.stdout.write('Successfully inserted "%s"\n' % str(new))

        elif remove:
            try:
                ua_to_remove = UserAgent.objects.get(ua_string=remove)
            except UserAgent.DoesNotExist:
                raise CommandError("No such UA string exists.")

            ua_to_remove.delete()
            self.stdout.write('Successfully removed "%s"\n' % str(remove))
        else:
            raise CommandError("You must give a valid parameter.")
