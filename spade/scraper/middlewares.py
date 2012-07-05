from scrapy.contrib.spidermiddleware.offsite import OffsiteMiddleware
from scrapy.http import Request
from scrapy.utils.httpobj import urlparse_cached
from scrapy import log

import spade.model.models as models

from urlparse import urlparse
import re

# Define middleware here

class CustomOffsiteMiddleware(OffsiteMiddleware):
    """
    Custom filtering middleware: ensures all requests are to internal links
    """

    def process_spider_output(self, response, result, spider):
        """Given a request, we figure out if we want it"""

        for req in result:
            if isinstance(req, Request):
                if req.dont_filter and self.should_follow(response, req):
                    yield req
                else:
                    domain = urlparse_cached(req).hostname
                    if domain and domain not in self.domains_seen[spider]:
                        log.msg("Filtered offsite request to %r: %s" % (domain, req),
                            level=log.DEBUG, spider=spider)
                        self.domains_seen[spider].add(domain)
            else:
                yield req

    def should_follow(self, response, request):
        """Determine if response.url and request.url have the same root url"""

        req_domain = urlparse_cached(response.url)
        res_domain = urlparse_cached(request.url)
        return req_domain.netloc == res_domain.netloc

    def spider_opened(self, spider):
        """Scrapy signal catching function: spider open"""
        self.domains_seen[spider] = set()

    def spider_closed(self, spider):
        """Scrapy signal catching function: spider close"""
        del self.domains_seen[spider]
