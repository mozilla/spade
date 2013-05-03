# General spider for retrieving site information

# Django Imports
from django.utils.timezone import utc

# Scrapy Imports
from scrapy import log
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from spade.scraper.items import MarkupItem
from spade.utils.misc import get_domain

# Utility Imports
from datetime import datetime
from hashlib import sha256
from urlparse import urljoin, urlparse
import os

# Django model
from spade import model


class GeneralSpider(BaseSpider):
    """
    A generic spider

    Crawls CSS, HTML, JS up to 1 level of depth from a given domain. Domains
    outside of the list provided are not crawled.
    """
    name = "all"

    def __init__(self):
        """
        Set URLs to traverse from
        """
        self._urls = []

    def get_now_time(self):
        """Gets a datetime"""
        # Convenience function for timezone-aware timestamps
        return datetime.utcnow().replace(tzinfo=utc)

    def log(self, msg):
        """Function for logging events"""
        log.msg(msg, level=log.DEBUG)

    @property
    def start_urls(self):
        if not self._urls:
            if not self.settings.get('URLS'):
                raise ValueError('No text file. Use -s URLS=somefile.txt')
            with open(self.settings.get('URLS')) as data:
                self._urls = list(set([line.rstrip('\r\n') for line in data]))
        return self._urls

    def start_requests(self):
        """convert start_urls to requests and return them"""
        for url in self.start_urls:
            for request in self.make_requests_from_url(url):
                yield request

    def make_requests_from_url(self, url):
        """
        Generates one request per user_agent
        """
        sitescan, _ = model.SiteScan.objects.get_or_create(
            batch=self.batch,
            site_url_hash=sha256(get_domain(url)).hexdigest(),
            defaults={'site_url': url})

        # Generate different UA requests for each UA
        for batch_user_agent in self.batch_user_agents:
            ua = batch_user_agent
            new_request = Request(url, dont_filter=True)
            new_request.headers.setdefault('User-Agent', ua.ua_string)
            new_request.meta['sitescan'] = sitescan
            new_request.meta['user_agent'] = ua
            self.log("Created request for {0} with ua {1}".format(
                                                        url, ua.ua_string))
            yield new_request

    def get_content_type(self, headers):
        """Gets a content type from the headers"""
        if headers:
            for h, val in headers.items():
                if h.lower().strip() == 'content-type':
                    # As it turns out, content-type often appears with some
                    # additional values e.g "text/css; charset=utf8" so we want
                    # just 'text/css' rather than the whole string
                    return val[0].split(";")[0]
        return ""

    def parse(self, response):
        """
        Function called by the scrapy downloader after a site url has been
        visited
        """
        content_type = self.get_content_type(response.headers)

        sitescan = response.meta.get('sitescan')

        if 'text/html' not in self.get_content_type(response.headers):

            # For linked content, find the urlscan it linked from
            urlscan = model.URLScan.objects.get(
                site_scan=sitescan,
                page_url_hash=sha256(response.meta['referrer']).hexdigest())
        else:
            # Only create urlscans for text/html
            urlscan, us_created = model.URLScan.objects.get_or_create(

                site_scan=sitescan,
                page_url_hash=sha256(response.url).hexdigest(),
                defaults={'page_url': response.url,
                          'timestamp': self.get_now_time()})

            # Continue crawling
            # Parse stylesheet links, scripts, and hyperlinks
            hxs = HtmlXPathSelector(response)

            # Extract other target links
            try:
                css_links = hxs.select('//link/@href').extract()
            except TypeError:
                css_links = []

            try:
                js_links = hxs.select('//script/@src').extract()
            except TypeError:
                js_links = []

            try:
                hyperlinks = hxs.select('//a/@href').extract()
            except TypeError:
                hyperlinks = []

            # Using a set removes duplicate links.
            all_links = set(hyperlinks + js_links + css_links)

            # Examine links, yield requests if they are valid
            for url in all_links:

                if not url.startswith('http://'):
                    # ensure that links are to real sites
                    if url.startswith('javascript:'):
                        continue
                    else:
                        url = urljoin(response.url, url)

                ua = response.meta['user_agent']

                request = Request(url)
                request.headers.setdefault('User-Agent', ua.ua_string)
                request.meta['referrer'] = response.url
                request.meta['sitescan'] = sitescan
                request.meta['user_agent'] = ua
                request.meta['content_type'] = None

                yield request

        # The response contains a user agent, we should yield an item
        item = MarkupItem()
        item['content_type'] = self.get_content_type(response.headers)
        item['filename'] = os.path.basename(urlparse(response.url).path)
        item['headers'] = unicode(response.headers)
        item['meta'] = response.meta
        item['raw_content'] = response.body
        item['sitescan'] = sitescan
        item['urlscan'] = urlscan
        item['url'] = response.url
        item['user_agent'] = response.meta.get('user_agent')
        item['redirected_from'] = response.meta.get('redirected_from',
                                                    u'')
        yield item
