# General spider for retrieving site information

from scrapy.spider import BaseSpider
import zlib
import json
import urlparse


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

    def set_user_agent(self, UA):
        self.user_agent = USER_AGENTS[UA]

    def get_start_urls(self):
        # Gets URLs to start crawl from
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
        # TODO: Put item model here, call save on the item model

        # STUB
        print response.body
        #print response.url
        #print response.headers
        #print self.get_content_type(response.headers)
        #print response.meta.get('referrer')
        #print USER_AGENT
