# General spider for retrieving site information

# Django Imports
from django.core.files.base import ContentFile
from django.core.management.base import CommandError
from django.utils.timezone import utc

# Scrapy Imports
from scrapy import log
from scrapy.conf import settings
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider

# Utility Imports
from datetime import datetime
from urlparse import urljoin, urlparse

import spade.model.models as models
import os


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

        # Default user agent, used to browse the structure of the site

        try:
            # Start from the first by default
            self.user_agent = self.user_agents[0]
        except IndexError:
            raise CommandError('No user agents have been set yet. '
                               'Need to add user agents.')

        self.curr_sitescan = None


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
        """Default spider callback function"""

        # Only create a sitescan object for each base site in the list
        if response.meta.get('referrer') is None:
            self.curr_sitescan = models.SiteScan()
            self.curr_sitescan.batch = self.batch
            self.curr_sitescan.site_url = response.url
            self.curr_sitescan.folder_name = urlparse(response.url).netloc
            self.curr_sitescan.save()

        # Generate a urlscan for this url
        urlscan = models.URLScan()
        urlscan.site_scan = self.curr_sitescan
        urlscan.page_url = response.url
        urlscan.timestamp = self.get_now_time()
        urlscan.save()

        # Define name of flatfiles used to save markup
        filename = os.path.basename(urlparse(response.url).path)

        headers = self.get_content_type(response.headers)
        if headers == None:
            headers = ""

        js_mimes = (
                     'text/javascript',
                     'application/x-javascript',
                     'application/javascript'
                   )

        # Scan 1 level (spider knows how in configs as long as we set referrer
        if 'text/html' in headers:
            # First save the request contents into a URLContent
            urlcontent = models.URLContent()
            urlcontent.url_scan = urlscan
            urlcontent.user_agent = self.user_agent

            # Store raw headers
            file_content = ContentFile(str(response.body))
            urlcontent.raw_markup.save(filename[:100]+"_html",file_content)
            urlcontent.raw_markup.close()

            # Store raw html
            file_content = ContentFile(str(response.headers))
            urlcontent.headers.save(filename[:100]+"_headers",file_content)
            urlcontent.headers.close()

            urlcontent.save()

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
                yield request

        elif any(a in headers for a in js_mimes):

            linkedjs = models.LinkedJS()
            linkedjs.url_scan = urlscan

            # Store raw js
            file_content = ContentFile(str(response.body))
            linkedjs.raw_js.save(filename+"_js",file_content)
            linkedjs.raw_js.save(filename[:100]+"_js",file_content)

            linkedjs.raw_js.close()

            linkedjs.save()

        elif 'text/css' in headers:
            linkedcss = models.LinkedCSS()
            linkedcss.url_scan = urlscan

            # Store raw css
            file_content = ContentFile(str(response.body))
            linkedcss.raw_css.save(filename[:100]+"_css",file_content)
            linkedcss.raw_css.close()

            linkedcss.save()


        # Update batch finish time, keep this last
        self.batch.finish_time = self.get_now_time()
        self.batch.save()
