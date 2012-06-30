from scrapy.contrib.spidermiddleware.offsite import OffsiteMiddleware
from scrapy.http import Request
from scrapy.utils.httpobj import urlparse_cached
from scrapy import log

import spade.model.models as models

from urlparse import urlparse
import re

# Define middleware here
USER_AGENTS = models.UserAgent.objects.all()

class PreRequestMiddleware(object):
    """
    This middleware allows us to define user agent based on the django database
    """

    def process_request(self, request, spider):
        """
        The dictionary "meta" is set by the spider, which distributes tasks
        with a list of UA strings -- we recursve over them here to scrape sites
        using every UA string in the list.
        """

        ua = spider.user_agent

        if request.meta.get('user_agent'):
            ua = request.meta['user_agent']

        request.headers.setdefault('User-Agent', ua)

        # Generate requests per user agent
        agent_index = request.meta.get('agent_index')
        if agent_index == None:
            agent_index = 0

            # Generate different UA responses
            while agent_index < len(USER_AGENTS):
                new_request = request.copy()
                new_request.headers.setdefault('User-Agent', USER_AGENTS[agent_index].ua_string)
                new_request.meta['agent_index'] = agent_index

                # Recurse
                agent_index = agent_index + 1
                self.process_request(new_request, spider)


class CustomOffsiteMiddleware(OffsiteMiddleware):
    """
    Custom filtering middleware: ensures all requests are to internal links
    """

    def process_spider_output(self, response, result, spider):
        """Given a request, we figure out if we want it"""

        for req in result:
            if isinstance(req, Request):
                if req.dont_filter or self.should_follow(response, req):
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

        req_domain = urlparse(response.url)
        res_domain = urlparse(request.url)

        return req_domain.netloc == res_domain.netloc

    def spider_opened(self, spider):
        """Scrapy signal catching function: spider open"""
        self.domains_seen[spider] = set()

    def spider_closed(self, spider):
        """Scrapy signal catching function: spider close"""
        del self.domains_seen[spider]
