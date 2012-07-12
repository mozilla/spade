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

# Define middleware here

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
                        self.domains_seen[spider].add(domain)
            else:
                yield req

    def should_follow(self, response, request):
        """
        We shouldn't follow a link if it goes offsite, with exception of .css
        and .js files because a lot of people use CDNs and the like to host
        their js and stylesheets.
        """
        req_domain = urlparse(response.url)
        res_domain = urlparse(request.url)

        extension = res_domain.path.split(".")[-1]
        if extension in ['css', 'js']:
            # Allow CSS and JS files
            return True

        # Otherwise, ensure that the domains share the same root origin
        return req_domain.netloc == res_domain.netloc

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

                content_type = request.meta['content_type'] or []

                # Allow inclusion of the correct depth of js/css or other
                # linked file up to 1 level deeper (this works by undoing the
                # depth counter by 1 for non-html files)
                if 'text/html' not in content_type:
                    depth = response.request.meta['depth']

                # Check if we need to filter
                if self.prio:
                    request.priority -= depth * self.prio
                if self.maxdepth and depth > self.maxdepth:
                    log.msg("Ignoring link (depth > %d): %s " % (self.maxdepth, request.url), \
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
