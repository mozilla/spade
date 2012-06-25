# General spider for retrieving site information

from django.core.files.base import ContentFile
from django.utils.timezone import utc

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy import log

from datetime import datetime
import json
import urlparse

# Django Models
import spade.model.models as models


class GeneralSpider(BaseSpider):
    # This class variable necessary for scrapy to detect this spider
    name="general"

    def __init__(self):
        # Initialize variables as instance vars to access instance methods
        self.allowed_domains = self.get_allowed_domains()
        self.start_urls = self.get_start_urls()

        # TODO: Do something about this.
        self.user_agent = "Mozilla/5.0"
        self.log("Using user agent "+str(self.user_agent))

        self.batch = models.Batch()
        self.batch.kickoff_time = self.get_now_time()
        self.batch.finish_time = self.get_now_time()
        self.batch.save()

        self.user_agents = models.UserAgent.objects.all()
        self.curr_sitescan = None


    def get_now_time(self):
        # Convenience function for timezone-aware timestamps
        return datetime.utcnow().replace(tzinfo=utc)


    def log(self, msg):
        # Debug function -- log messages
        log.msg(msg, level=log.DEBUG)


    def get_start_urls(self):
        # List of URLs to crawl from (descending to 1 level from these sites)
        start_urls = []
        for crawllist in models.CrawlList.objects.all():
            start_urls.append(crawllist.url)
        return start_urls


    def get_allowed_domains(self):
        # Make all the URLs we started at "allowed"
        self.allowed_domains = []
        for domain in self.get_start_urls():
            self.allowed_domains.append(urlparse.urlsplit(domain)[1])

        return self.allowed_domains


    def get_content_type(self, headers):
        # Get's a content type from the headers
        if headers:
            for h in headers:
                if h.lower().strip() == 'content-type':
                    return headers[h]


    def desired_content_type(self, content_type):
        # Reject anything not CSS/HTML/JS
        target_types = [
                        'text/html',
                        'text/css',
                        'application/x-javascript',
                        'text/javascript',
                        'application/javascript',
                       ]

        if content_type in target_types:
            return True
        else:
            return False


    # Called when any URL is being parsed
    def parse(self, response):
        # Only create a sitescan object for each base site in the list
        if response.meta.get('referrer') is None:
            self.curr_sitescan = models.SiteScan()
            self.curr_sitescan.batch = self.batch
            self.curr_sitescan.timestamp = self.get_now_time()
            self.curr_sitescan.site_url = response.url
            self.curr_sitescan.save()

        # Generate a urlscan for this url
        urlscan = models.URLScan()
        urlscan.site_scan = self.curr_sitescan
        urlscan.page_url = response.url
        urlscan.save()

        # Define name of flatfiles used to save markup
        filename = str(response.url)

        # Scan 1 level (spider knows how in configs as long as we set referrer
        if 'text/html' in self.get_content_type(response.headers):
            # First save the request contents into a URLContent
            urlcontent = models.URLContent()
            urlcontent.url_scan = urlscan
            urlcontent.user_agent = self.user_agent

            # Store raw headers
            file_content = ContentFile(str(response.body))
            urlcontent.raw_markup.save(filename+"_html",file_content)
            urlcontent.raw_markup.close()

            # Store raw html
            file_content = ContentFile(str(response.headers))
            urlcontent.headers.save(filename+"_headers",file_content)
            urlcontent.headers.close()

            urlcontent.save()

            # Parse stylesheet links, scripts, and hyperlinks
            hxs = HtmlXPathSelector(response)
            for url in hxs.select('//link/@href').extract() + \
                hxs.select('//script/@src').extract() + \
                hxs.select('//a/@href').extract():

                if not url.startswith('http://'):
                    # ensure that links are to real sites
                    if url.startswith('javascript:'):
                        # the "a href" was not a real url link, skip this one!
                        continue
                    else:
                        url = urlparse.urljoin(response.url,url)

                # Log what link we're parsing for debug purposes
                self.log(url)

                # Make Request & set referrer (else spider can't 1-level crawl)
                request = Request(url, callback=self.parse)
                request.meta['referrer'] = response.url
                yield request

        elif 'text/javascript' in self.get_content_type(response.headers):
            linkedjs = models.LinkedJS()
            linkedjs.url_scan = urlscan

            # Store raw js
            file_content = ContentFile(str(response.body))
            linkedjs.raw_js.save(filename+"_js",file_content)
            linkedjs.raw_js.close()

            linkedjs.save()

        elif 'text/css' in self.get_content_type(response.headers):
            linkedcss = models.LinkedCSS()
            linkedcss.url_scan = urlscan

            # Store raw css
            file_content = ContentFile(str(response.body))
            linkedcss.raw_css.save(filename+"_css",file_content)
            linkedcss.raw_css.close()

            linkedcss.save()


        # Update batch finish time, keep this last
        self.batch.finish_time = self.get_now_time()
        self.batch.save()
