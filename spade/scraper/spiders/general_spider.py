"""
General spider for retrieving site information
"""

# Django Imports
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
        now = self.get_now_time()

        # Create initial batch
        self.batch = model.Batch.objects.create(
            kickoff_time=now, finish_time=now)
        self.batch.save()

        self.user_agents = list(model.UserAgent.objects.all())
        self.start_urls = self.get_start_urls()

    def get_now_time(self):
        """Gets a datetime"""
        # Convenience function for timezone-aware timestamps
        return datetime.utcnow().replace(tzinfo=utc)

    def log(self, msg):
        """Function for logging events"""
        log.msg(msg, level=log.DEBUG)

    def get_start_urls(self):
        """Extracts urls from a text file into the list of URLs to crawl"""
        if not settings.get('URLS'):
            raise ValueError('No text file. Use -s URLS=somefile.txt')

        with open(settings.get('URLS')) as data:
            return [line.rstrip('\r\n') for line in data]

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

    def start_requests(self):
        """Overrides a scrapy function to generate the requests array"""
        reqs = []
        for url in self.start_urls:
            request_generator = self.make_requests_from_url(url)
            for request in request_generator:
                reqs.append(request)
        return reqs

    def make_requests_from_url(self, url):
        """
        Override a scrapy function to replace the initial request (no UA) with
        many requests using different ua strings
        """
        for user_agent in list(model.UserAgent.objects.all()):
            request = Request(url, dont_filter=True)
            request.meta['referrer'] = None
            request.meta['sitescan'] = None
            request.meta['user_agent'] = user_agent
            request.headers.setdefault('User-Agent', user_agent)

            yield request

    def parse(self, response):
        """
        Function called by the scrapy downloader after a site url has been
        visited
        """
        content_type = self.get_content_type(response.headers)

        sitescan = response.meta.get('sitescan')
        if sitescan is None:
            # This sitescan needs to be created
            sitescan, ss_created = model.SiteScan.objects.get_or_create(
                batch=self.batch,
                site_url_hash=sha256(response.url).hexdigest(),
                defaults={'site_url': response.url})

            if not ss_created:
                # Duplicate URL in the text file, ignore this site
                return

        if 'text/html' == content_type:
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

            # Ensure links are valid urls
            for url in all_links:

                if not url.startswith('http://'):
                    # ensure that links are to real sites
                    if url.startswith('javascript:'):
                        continue
                    else:
                        url = urljoin(response.url, url)

                # Generate requests for each new url found
                request = Request(url)
                request.meta['referrer'] = response.url
                request.meta['sitescan'] = sitescan
                request.meta['user_agent'] = response.meta.get('user_agent')
                request.dont_filter = True

                yield request

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

        yield item
