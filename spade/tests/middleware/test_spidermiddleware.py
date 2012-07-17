from scrapy.conf import settings
from scrapy.http import Response, Request

from spade import model
from spade.tests.model import factories
from spade.scraper.middlewares import CustomDepthMiddleware
from spade.scraper.middlewares import CustomOffsiteMiddleware
from spade.scraper.spiders.general_spider import GeneralSpider


def pytest_funcarg__spider(request):
    """Initialize a dummy spider"""
    spider = GeneralSpider()
    now = spider.get_now_time()
    spider.batch = model.Batch.objects.create(
        kickoff_time=now, finish_time=now)
    spider.batch.save()

    return spider


def pytest_funcarg__scrape_request(request):
    mock_request = Request('http://test:12345')
    mock_request.meta['referrer'] = None
    mock_request.meta['sitescan'] = None
    mock_request.meta['user_agent'] = None
    mock_request.dont_filter = True
    return mock_request


def pytest_funcarg__mock_response(request):
    scrape_request = request.getfuncargvalue("scrape_request")
    mock_response = Response('http://test.com')
    mock_response.request = scrape_request
    return mock_response


def generate_requests():
    """Generate one request that should be filtered, and one that shouldnt"""
    mock_request = Request('http://google.com/')
    mock_request.meta['referrer'] = 'http://test.com'
    mock_request.meta['sitescan'] = None
    mock_request.meta['user_agent'] = None
    mock_request.dont_filter = True
    yield mock_request

    mock_request = Request('http://test.com/hello.html')
    mock_request.meta['referrer'] = 'http://test.com'
    mock_request.meta['sitescan'] = None
    mock_request.meta['user_agent'] = None
    mock_request.dont_filter = True
    yield mock_request


def pytest_funcarg__offsite_middleware(request):
    offsite_middleware = CustomOffsiteMiddleware()
    return offsite_middleware


def pytest_funcarg__depth_middleware(request):
    depth_middleware = CustomDepthMiddleware(maxdepth=2)
    return depth_middleware


def test_offsitefilter(spider, offsite_middleware, mock_response):
    """Ensure offsite links are not crawled"""
    offsite_middleware.spider_opened(spider)
    request_generator = generate_requests()


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


def test_crawl_1level(depth_middleware):
    """Ensure we only download 1 level of html"""
    depth_middleware.
    # This test needs to insert a request into the downloader middleware and
    # ensure that no response comes out of the downloader
    assert False


#def test_crawl_linked_morelevels(depth_middleware):
#    """Ensure all CSS/JS is downloaded on crawled html pages"""
#    # This test needs to insert a request into the downloader middleware and
#    # ensure that a valid response comes out
#    assert False
