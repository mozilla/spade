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
                    help='Added user-agent will be primary mobile UA (the UA we want to be sure sites are sniffing for)'),
        make_option('--desktop',
                    action='store_true',
                    dest='desktop',
                    default=False,
                    help='Added user-agent is a desktop UA'),
        )

    def handle(self, *args, **options):

        new = options.get('add')
        remove = options.get('remove')
        primary = options.get('primary')
        desktop = options.get('desktop')

        if options.get('list'):
            self.stdout.write("\n")
            self.stdout.write("These UAs will be used for the next scan:\n")
            self.stdout.write("=========================================\n")

            for agent in UserAgent.objects.all():
                self.stdout.write("%s\n" % agent)

        elif new:
            if primary:
                if desktop:
                    raise CommandError("The primary UA must be a mobile UA")
                # only one UA can be primary
                UserAgent.objects.update(primary_ua=False)

            if desktop:
                ua_type = UserAgent.DESKTOP
            else:
                ua_type = UserAgent.MOBILE

            new_ua = UserAgent.objects.create(
                ua_string=str(new), primary_ua=primary, ua_type=ua_type)
            self.stdout.write('Successfully inserted "%s"\n' % new_ua)

        elif remove:
            try:
                ua_to_remove = UserAgent.objects.get(ua_string=remove)
            except UserAgent.DoesNotExist:
                raise CommandError("No such UA string exists.")

            ua_to_remove.delete()
            self.stdout.write('Successfully removed "%s"\n' % str(remove))
        else:
            raise CommandError("You must give a valid parameter.")
