"""
Just a thin wrapper around scrapy, so we can run it as a management command.

"""
from __future__ import absolute_import

from django.core.management.base import BaseCommand
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from scrapy import log


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
            settings = Settings()
            settings.overrides['URLS'] = args[0]
            crawler = Crawler(settings)
            crawler.configure()
            crawler.crawl(spider)
            crawler.start()
            log.start()
            reactor.run()
