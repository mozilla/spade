"""
Custom middleware for scrapy
"""
from scrapy.contrib.spidermiddleware import offsite, depth
from scrapy.http import Request
from scrapy.utils.httpobj import urlparse_cached
from scrapy import log


def has_extension(response_or_request, ext):
    return urlparse_cached(response_or_request).path.split(".")[-1] == ext


class OffsiteMiddleware(offsite.OffsiteMiddleware):
    """Filtering middleware that ensures all requests are to internal links."""
    def process_spider_output(self, response, result, spider):
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
        """Only follow offsite links to JS and CSS files, not new pages."""
        res_url_data = urlparse_cached(response)
        req_url_data = urlparse_cached(request)

        if has_extension(request, 'js') or has_extension(request, 'css'):
            return True

        # Otherwise, ensure that the domains share the same root origin
        return req_url_data.netloc == res_url_data.netloc



class DepthMiddleware(depth.DepthMiddleware):
    """A depth middleware that exempts JS files."""
    def process_spider_output(self, response, result, spider):
        """Ignore depth restrictions for JS links."""
        check_depth = []
        for req in result or []:
            if isinstance(req, Request) and has_extension(req, 'js'):
                yield req
            else:
                check_depth.append(req)
        for req in super(DepthMiddleware, self).process_spider_output(
                response, check_depth, spider):
            yield req
