# General spider for retrieving site information

# Django Imports
from django.core.management.base import CommandError
from django.utils.timezone import utc

# Scrapy Imports
from scrapy import log
from scrapy.conf import settings
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from spade.scraper.items import MarkupItem

# Utility Imports
from datetime import datetime
from urlparse import urljoin, urlparse
import os

# Django Models
import spade.model.models as models


class GeneralSpider(BaseSpider):
    """
    A generic spider

    Crawls CSS, HTML, JS up to 1 level of depth from a given domain. Domains
    outside of the list provided are not crawled.
    """
    name="all"

    def __init__(self):
        """
        Initialization

        Get list of user agents, allowed domains, start urls as well as create
        a new batch to represent a single scraper run.
        """
        # Initialize variables as instance vars to access instance methods
        self.start_urls = self.get_start_urls()


        self.batch = models.Batch()
        self.batch.kickoff_time = self.get_now_time()
        self.batch.finish_time = self.get_now_time()
        self.batch.save()

        self.user_agents = models.UserAgent.objects.all()

    def get_now_time(self):
        """Gets a datetime"""
        # Convenience function for timezone-aware timestamps
        return datetime.utcnow().replace(tzinfo=utc)


    def log(self, msg):
        """Function for logging events"""
        log.msg(msg, level=log.DEBUG)


    def get_start_urls(self):
        """Extracts urls from a text file into the list of URLs to crawl"""
        if settings.get('URLS') == None:
            raise CommandError('No text file. Use -s URLS=somefile.txt')
        else:
            try:
                start_urls = []
                with open(settings.get('URLS')) as data:
                    datalines = (line.rstrip('\r\n') for line in data)
                    for line in datalines:
                        start_urls.append(line)
            except IOError:
                raise CommandError('No such file exists!')

            return start_urls

    def get_content_type(self, headers):
        """Get's a content type from the headers"""
        if headers:
            for h in headers:
                if h.lower().strip() == 'content-type':
                    return headers[h]


    def parse(self, response):
        headers = self.get_content_type(response.headers)
        if headers == None:
            headers = ""

        if response.meta.get('user_agent') == None:
            # Ensure user agents have been set
            if len(self.user_agents) == 0:
                raise CommandError('No user agents have been set yet. '
                                   'Need to add user agents.')

            # Generate different UA requests for each UA
            agent_index = 0
            while agent_index < len(self.user_agents):
                ua = self.user_agents[agent_index].ua_string

                # Generate new request
                new_request = Request(response.url)
                new_request.meta['referrer'] = None
                new_request.headers.setdefault('User-Agent', ua)
                new_request.meta['user_agent'] = ua
                new_request.dont_filter = True

                agent_index = agent_index + 1
                yield new_request

            # Continue crawling
            if 'text/html' in headers:
                # Parse stylesheet links, scripts, and hyperlinks
                hxs = HtmlXPathSelector(response)

                # Extract other target links
                try:
                    css_links  = hxs.select('//link/@href').extract()
                except TypeError:
                    css_links = []

                try:
                    js_links   = hxs.select('//script/@src').extract()
                except TypeError:
                    js_links = []

                try:
                    hyperlinks = hxs.select('//a/@href').extract()
                except TypeError:
                    hyperlinks = []

                # Examine links, yield requests if they are valid
                all_links = hyperlinks + js_links + css_links
                for url in all_links:

                    if not url.startswith('http://'):
                        # ensure that links are to real sites
                        if url.startswith('javascript:'):
                            continue
                        else:
                            url = urljoin(response.url,url)

                    request = Request(url)
                    request.meta['referrer'] = response.url
                    request.meta['user_agent'] = None
                    request.dont_filter = True

                    yield request

        else:
            # The response contains a user agent, we should yield an item
            item = MarkupItem()
            item['raw_markup'] = response.body
            item['headers'] = unicode(response.headers)
            item['user_agent'] = response.meta.get('user_agent')
            item['meta'] = response.meta
            item['filename'] = os.path.basename(urlparse(response.url).path)
            item['url'] = response.url
            yield item
