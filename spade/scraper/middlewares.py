"""
Custom middleware for scrapy
"""
from scrapy.contrib.spidermiddleware.offsite import OffsiteMiddleware
from scrapy.exceptions import ScrapyDeprecationWarning
from scrapy.http import Request
from scrapy import log
from scrapy.utils.httpobj import urlparse_cached
from scrapy import log
from urlparse import urlparse

import spade.model.models as models
import re
import warnings


class CustomOffsiteMiddleware(OffsiteMiddleware):
    """
    Custom filtering middleware: ensures all requests are to internal links
    """

    def process_spider_output(self, response, result, spider):
        """Given a request, we figure out if we want it"""
        for req in result:
            if isinstance(req, Request):
                if self.should_follow(response, req):
                    yield req
                else:
                    domain = urlparse_cached(req).hostname
                    if domain and domain not in self.domains_seen[spider]:
                        log.msg("Filtered offsite request to %r: %s" % (domain, req),
                                level=log.DEBUG, spider=spider)

                        # Mark the domain as seen in the scrapy cache
                        self.domains_seen[spider].add(domain)
            else:
                yield req

    def should_follow(self, response, request):
        """
        We shouldn't follow a link if it goes offsite, with exception of .css
        and .js files because a lot of people use CDNs and the like to host
        their js and stylesheets.
        """
        res_url_data = urlparse(response.url)
        req_url_data = urlparse(request.url)

        extension = req_url_data.path.split(".")[-1]
        if extension in ['css', 'js']:
            # Allow CSS and JS files
            return True

        # Otherwise, ensure that the domains share the same root origin
        return req_url_data.netloc == res_url_data.netloc

    def spider_opened(self, spider):
        """Scrapy signal catching function: spider open"""
        self.domains_seen[spider] = set()

    def spider_closed(self, spider):
        """Scrapy signal catching function: spider close"""
        del self.domains_seen[spider]


class CustomDepthMiddleware(object):

    def __init__(self, maxdepth, stats=None, verbose_stats=False, prio=1):
        self.maxdepth = maxdepth
        self.stats = stats
        self.verbose_stats = verbose_stats
        self.prio = prio

    @classmethod
    def from_settings(cls, settings):
        maxdepth = settings.getint('DEPTH_LIMIT')
        usestats = settings.getbool('DEPTH_STATS')
        verbose = settings.getbool('DEPTH_STATS_VERBOSE')
        prio = settings.getint('DEPTH_PRIORITY')
        if usestats:
            from scrapy.stats import stats
        else:
            stats = None
        return cls(maxdepth, stats, verbose, prio)

    def process_spider_output(self, response, result, spider):
        def _filter(request):
            if isinstance(request, Request):
                depth = response.request.meta['depth'] + 1
                request.meta['depth'] = depth

                # Check if we need to filter
                if self.prio:
                    request.priority -= depth * self.prio
                if self.maxdepth and depth > self.maxdepth:
                    log.msg("Ignoring link (depth > %d): %s " % (self.maxdepth, request.url),
                            level=log.DEBUG, spider=spider)
                    return False
                elif self.stats:
                    if self.verbose_stats:
                        self.stats.inc_value('request_depth_count/%s' % depth, spider=spider)
                    self.stats.max_value('request_depth_max', depth, spider=spider)
            return True

        # base case (depth=0)
        if self.stats and 'depth' not in response.request.meta:
            response.request.meta['depth'] = 0
            if self.verbose_stats:
                self.stats.inc_value('request_depth_count/0', spider=spider)

        return (r for r in result or () if _filter(r))

class UARequestMiddleware(object):
    """
    Spawn user agent requests.
    """
    def process_spider_output(self, response, result, spider):
        def _request_generator(requests):
            for request in requests:
                # If it is a request, replace it with x user agent requests
                if isinstance(request, Request):
                    for user_agent in spider.user_agents:
                        new_request = Request(request.url)
                        new_request.meta['referrer'] = request.meta.get('referrer')
                        new_request.meta['sitescan'] = request.meta.get('sitescan')
                        new_request.meta['user_agent'] = user_agent
                        new_request.headers.setdefault('User-Agent', user_agent)
                        new_request.dont_filter = True
                        yield new_request
                # If it is an item being sent to the pipeline, just leave it be
                yield request

        return _request_generator(result)
