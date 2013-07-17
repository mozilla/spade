"""
Just a thin wrapper around scrapy, so we can run it as a management command.

"""
from __future__ import absolute_import

from django.core.management.base import BaseCommand
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings
from scrapy import log, signals
from spade.scraper.spiders.general_spider import GeneralSpider


def stop_reactor():
    reactor.stop()


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
            settings = get_project_settings()
            settings.overrides['URLS'] = args[0]
            crawler = Crawler(settings)
            spider = GeneralSpider()
            crawler.configure()
            crawler.crawl(spider)
            crawler.start()
            log.start_from_crawler(crawler)

            # stop the reactor once the spider has finished
            crawler.signals.connect(reactor.stop, signal=signals.spider_closed)

            try:
                log.msg("Running reactor...")
                reactor.run()
            except KeyboardInterrupt:
                stop_reactor()
            finally:
                log.msg("Reactor stopped")
                log.msg("#" * 40)
