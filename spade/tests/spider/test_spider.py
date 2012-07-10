from scrapy.conf import settings
from scrapy.http import Response, Request
from spade.scraper.spiders.general_spider import GeneralSpider
from spade import model
from spade.scraper.items import MarkupItem

def pytest_funcarg__spider(request):
    """Use scrapy's overrides to start the spider w/ specific settings"""
    # Create 2 User agents
    ua1 = model.UserAgent()
    ua1.ua_string = 'Firefox / 11.0'
    ua1.save()

    ua1 = model.UserAgent()
    ua1.site_url = 'Chrome / 20.0'
    ua1.save()

    settings.overrides['LOG_ENABLED'] = True
    settings.overrides['URLS'] = "spade/tests/sitelists/urls.txt"
    spider = GeneralSpider()
    spider.user_agents = list(model.UserAgent.objects.all())

    # Create initial batch
    now = spider.get_now_time()
    spider.batch = model.Batch.objects.create(
        kickoff_time=now, finish_time=now)
    spider.batch.save()

    return spider

def test_spider_name(spider):
    """Ensure the spider's name is correct"""
    assert spider.name == "all"

def test_spider_read_from_file(spider):
    """Ensure the test list of urls was read correctly"""
    if len(spider.start_urls) != 1:
        assert False
    elif spider.start_urls[0] == "http://localhost:8181":
        assert True
    else:
        assert False

def test_useragents_spider(spider, httpserver):
    """Ensure multiple requests with different user agent strings are emitted"""

    mock_html = """
                <html>
                <head></head>
                <body>
                <a href="link1.html">Link 1</a>
                <a href="link2.html">Link 2</a>
                </body></html>
                """

    mock_headers = {'Content-Length': ['220'],
                    'X-Powered-By': ['PHP/5.3.2-1ubuntu4.17'],
                    'Vary': ['Accept-Encoding'],
                    'Server': ['Apache/2.2.14 (Ubuntu)'],
                    'Connection': ['close'],
                    'Date': ['Tue, 10 Jul 2012 21:52:28 GMT'],
                    'Content-Type': ['text/html']}

    httpserver.serve_content(content=mock_html,
                             code=200,
                             headers=mock_headers)

    # Create a mock request
    mock_request = Request(httpserver.url)
    mock_request.meta['referrer'] = None
    mock_request.meta['sitescan'] = None
    mock_request.meta['user_agent'] = None
    mock_request.dont_filter = True


    # Create a mock response linked to the request
    mock_response = Response(httpserver.url, body=mock_html)
    mock_response.flags = []
    mock_response.request = mock_request
    mock_response.status = 200
    mock_response.headers = mock_headers
    mock_response.encoding = 'ascii'

    generator = spider.parse(mock_response)

    items = 0
    requests = 0
    for item in generator:
        if isinstance(item, Request):
            requests = requests + 1
            # TODO: Inspect each request for correct user agents
        if isinstance(item, MarkupItem):
            items = items + 1

    assert (items == 0) and (requests == 4)


#def test_savedcontent(spider):
#    """Ensure html, css, and javascript are saved correctly"""
#    # Look at items emitted after spider crawls a stub page to ensure that
#    # items for CSS, JS, and HTML are all emitted
#    assert False
#
#def test_useragents_downloader(spider):
#    """Ensure the downloader uses useragents given to it """
#    # Mock requests with different UAs and see the response UA is the same.
#    # This could be further tested with an actual web server that responds
#    # differently to different UAs
#    assert False
#
#def test_duplinks(spider):
#    """Ensure pages containing two of the same link only visit once / save 1"""
#    # The downloader will issue two responses to the spider, with the same link
#    # Ensure that we filter out the responses in the spider, since the scrapy
#    # core dupfilter is disabled.
#    assert False
