"""
Just a thin wrapper around scrapy, so we can run it as a management command.

"""
from __future__ import absolute_import

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def run_from_argv(self, argv):
        self._argv = argv
        self.execute()

    def handle(self, *args, **options):
        from scrapy.cmdline import execute

        # Take a filename from command line to crawl
        default = [u""]
        default.append(u"crawl")
        default.append(u"all")
        default.append(u"-s")
        default.append(u"URLS="+unicode(self._argv[2]))
        execute(default)
