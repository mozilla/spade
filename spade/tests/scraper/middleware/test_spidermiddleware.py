from scrapy.http import Response, Request
from spade import model
from spade.scraper.middlewares import DepthMiddleware
from spade.scraper.middlewares import OffsiteMiddleware


def pytest_funcarg__offsite_middleware(request):
    offsite_middleware = OffsiteMiddleware()
    return offsite_middleware


def pytest_funcarg__depth_middleware(request):
    depth_middleware = DepthMiddleware(maxdepth=2)
    return depth_middleware


def pytest_funcarg__scrape_request(request):
    """A first-time scrape request with no settings"""
    mock_request = Request('http://test.com')
    mock_request.meta['referrer'] = None
    mock_request.meta['sitescan'] = None
    mock_request.meta['user_agent'] = None
    return mock_request


def pytest_funcarg__mock_response(request):
    """
    Fake response to the scrape request -- we only fill out the fields used by
    the middleware for testing purposes
    """
    scrape_request = request.getfuncargvalue("scrape_request")
    mock_response = Response('http://test.com')
    mock_response.request = scrape_request
    return mock_response


def pytest_funcarg__depth1_request(request):
    """Modified scrape request with stubbed depth = 1"""
    mock_request = request.getfuncargvalue("scrape_request")
    mock_request.replace(url='http://test.com/home')
    mock_request.meta['referrer'] = 'http://test.com'
    mock_request.meta['depth'] = 1
    return mock_request


def pytest_funcarg__depth2_request(request):
    """Modified scrape request with stubbed depth = 2"""
    mock_request = request.getfuncargvalue("scrape_request")
    mock_request.replace(url='http://test.com/home/fun')
    mock_request.meta['referrer'] = 'http://test.com/home'
    mock_request.meta['depth'] = 2
    return mock_request


def generate_offsite_testing_requests():
    """Generate one request that should be filtered, and one that shouldnt"""
    # This should be filtered
    mock_request = Request('http://google.com/')
    mock_request.meta['referrer'] = 'http://test.com'
    yield mock_request

    # This shouldn't be filtered
    mock_request = Request('http://test.com/hello.html')
    mock_request.meta['referrer'] = 'http://test.com'
    yield mock_request


def generate_crawl_html_requests():
    """Generate an arbitrary request"""
    mock_request = Request('http://test.com/hello.html')
    mock_request.meta['referrer'] = 'http://test.com'
    mock_request.meta['content_type'] = "text/html"
    yield mock_request


def generate_crawl_js_and_css_requests():
    """Generate one JS and one CSS request. Both should not be filtered."""
    # JS Request
    mock_request = Request('http://test.com/jquery.js')
    mock_request.meta['referrer'] = 'http://test.com'
    mock_request.meta['content_type'] = "text/javascript"
    yield mock_request

    # CSS Request
    mock_request = Request('http://test.com/styles/style.css')
    mock_request.meta['referrer'] = 'http://test.com'
    mock_request.meta['content_type'] = "text/css"
    yield mock_request


def test_offsitefilter(spider, offsite_middleware, mock_response):
    """Ensure offsite links are not crawled"""
    offsite_middleware.spider_opened(spider)
    request_generator = generate_offsite_testing_requests()

    # Call the middleware on the generator: it should filter offsite requests
    remaining_requests = offsite_middleware.process_spider_output(
        mock_response, request_generator, spider)

    # Collect results
    results = []
    for req in remaining_requests:
        results.append(req)

    offsite_middleware.spider_closed(spider)

    assert results[0].url == 'http://test.com/hello.html'
    assert len(results) == 1


def test_crawl_1level(spider, depth_middleware, mock_response, depth1_request):
    """Ensure that 1 level crawling is allowed"""
    request_generator = generate_crawl_html_requests()

    # Depth of the requests in the generator is decided by the previous request
    # depth + 1. So to test that level 2 links are accepted, we give previous
    # depth = 1 using a "depth1 request"
    mock_response.request = depth1_request

    remaining_requests = depth_middleware.process_spider_output(
        mock_response, request_generator, spider)

    results = []
    for req in remaining_requests:
        results.append(req)

    # Assert that the one request in the generator went through
    assert len(results) == 1


def test_crawl_limit(spider, depth_middleware, mock_response, depth2_request):
    """Ensure that 2 or more levels of crawling for html is not allowed"""
    request_generator = generate_crawl_html_requests()

    # Depth of the requests in the generator is decided by the previous request
    # depth + 1. So to test that level > 2 links are rejected, we give previous
    # depth = 2 using a "depth2 request"
    mock_response.request = depth2_request

    remaining_requests = depth_middleware.process_spider_output(
        mock_response, request_generator, spider)

    results = []
    for req in remaining_requests:
        results.append(req)

    # Assert no requests went through
    assert len(results) == 0


def test_linkedpages(spider, depth_middleware, mock_response, depth2_request):
    """
    Ensure only JS requests are not filtered when linked from level 2 html
    pages
    """
    request_generator = generate_crawl_js_and_css_requests()

    mock_response.request = depth2_request

    remaining_requests = depth_middleware.process_spider_output(
        mock_response, request_generator, spider)

    results = []
    for req in remaining_requests:
        results.append(req)

    assert len(results) == 1
