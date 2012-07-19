"""
Just a thin wrapper around scrapy, so we can run it as a management command.

"""
from __future__ import absolute_import

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    args = "<newline delimited textfile of URLs to scrape>"
    help = (
        u"  Scrapes and parses html/css properties down to 1-level\n"
        u"  on each site from the specified text file\n")

    def handle(self, *args, **options):
        if (not len(args) == 1) or (args[0] == u"help"):
            self.stdout.write(u"Usage: {0}\n".format(self.args))
            self.stdout.write(self.help)
        else:
            # Take a filename from command line to crawl
            default = [u""]
            default.append(u"crawl")
            default.append(u"all")
            default.append(u"-s")
            default.append(u"URLS=" + unicode(args[0]))

            from scrapy.cmdline import execute
            execute(default)
