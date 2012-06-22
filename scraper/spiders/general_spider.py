# General spider for retrieving site information

from datetime import datetime
from django.utils.timezone import utc
from scrapy.spider import BaseSpider
from scrapy import log
import json
import urlparse

#from scraper.items import BatchItem
import spade.model.models as models


# TODO: Make these user agents come from database
USER_AGENTS = {
               'FF12_1':("Mozilla/5.0 (Android; Mobile; rv:12.0) ",
                      "Gecko/12.0 Firefox/12.0"
                     ),
               'FF12_2':("Mozilla/5.0 (Gonk; Mobile; rv:12.0) ",
                     "Gecko/12.0 Firefox/12.0"
                     ),
               'FF12_3':("Mozilla/5.0 (Gonk, like Android; Mobile; rv:12.0) ",
                      "Gecko/12.0 Firefox/12.0"
                     ),
               'FF12_4':("Mozilla/5.0 (Gonk, like iPhone; Mobile; rv:12.0) ",
                      "Gecko/12.0 Firefox/12.0"
                     ),
               'IPHONE':("Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS ",
                         "X) AppleWebKit/534.46 (KHTML, like Gecko)",
                         "Version/5.1 Mobile/9A334 Safari/7534.48.32"
                        ),
               'ANDROID':("Mozilla/5.0 (Linux; U; Android 4.0; en-us; ",
                          "Tuna Build/IFK77E) AppleWebKit/534.30 (KHTML, ",
                          "like Gecko) Version/4.0 Mobile Safari/534.67"
                         )
              }

class GeneralSpider(BaseSpider):
    # This class variable necessary for scrapy to detect this spider
    name="general"

    def __init__(self):
        # Initialize variables as instance vars to access instance methods
        self.allowed_domains = self.get_allowed_domains()
        self.start_urls = self.get_start_urls()

        # TODO: Ideally for a site we use every UA in a table
        self.set_user_agent('IPHONE')
        log.msg("Using user agent "+str(self.user_agent), level=log.DEBUG)

        self.batch = models.Batch()
        self.batch.kickoff_time = self.get_now_time()

    def get_now_time(self):
        # Convenience function for timezone-aware timestamps
        return datetime.utcnow().replace(tzinfo=utc)

    def set_user_agent(self, UA):
        # Set the user agent
        self.user_agent = "".join(USER_AGENTS[UA])

    def get_start_urls(self):
        # Gets URLs to start crawl from
        # TODO: get urls from database
        start_urls = [
            # This page gives the user agent that visited it
            "http://ambushnetworks.com/test.php",
        ]
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


    def parse(self, response):
        # Called when a URL is being parsed
        self.batch.finish_time = self.get_now_time()
        self.batch.save()

        print response.body
        #print response.url
        #print response.headers                                                                                                                                              from spade.model.models import Batch, SiteScan, URLScan, URLContent, LinkedCSS, UserAgent
        #print self.get_content_type(response.headers)
        #print response.meta.get('referrer')
        #print USER_AGENT
