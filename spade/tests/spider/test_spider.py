from scrapy.conf import settings
from scrapy.http import Response, Request
from spade.scraper.spiders.general_spider import GeneralSpider
from spade import model
from spade.scraper.items import MarkupItem

def pytest_funcarg__spider(request):
    """Use scrapy's overrides to start the spider w/ specific settings"""
    settings.overrides['LOG_ENABLED'] = True
    settings.overrides['URLS'] = u"spade/tests/sitelists/urls.txt"
    spider = GeneralSpider()

    # Create initial batch
    now = spider.get_now_time()
    spider.batch = model.Batch.objects.create(
        kickoff_time=now, finish_time=now)
    spider.batch.save()

    return spider

def pytest_funcarg__html_headers(request):
    html_headers = {'X-Powered-By': ['PHP/5.3.2-1ubuntu4.17'],
                    'Vary': ['Accept-Encoding'],
                    'Server': ['Apache/2.2.14 (Ubuntu)'],
                    'Connection': ['close'],
                    'Date': ['Tue, 10 Jul 2012 21:52:28 GMT'],
                    'Content-Type': ['text/html']}
    return html_headers

def pytest_funcarg__scrape_request(request):
    # Create a mock request
    mock_request = Request('http://test:12345')
    mock_request.meta['referrer'] = None
    mock_request.meta['sitescan'] = None
    mock_request.meta['user_agent'] = None
    mock_request.dont_filter = True
    return mock_request

def pytest_funcarg__mock_html_twolinks(request):
    mock_html = """
                <html>
                <head></head>
                <body>
                <a href="link1.html">Link 1</a>
                <a href="link2.html">Link 2</a>
                </body></html>
                """
    return mock_html

def pytest_funcarg__mock_html_nolinks(request):
    mock_html = """
                <html>
                <head></head>
                <body>
                </body></html>
                """
    return mock_html


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

def test_useragents_spider(spider, scrape_request, html_headers,
                           mock_html_nolinks):
    """Ensure multiple requests with different user agent strings emitted"""
    # Create 2 useragents
    ua1 = model.UserAgent()
    ua1.ua_string = u'Firefox / 11.0'
    ua1.save()

    ua2 = model.UserAgent()
    ua2.ua_string = u'Chrome / 20.0'
    ua2.save()
    spider.user_agents = list(model.UserAgent.objects.all())

    # Generate a mock response
    mock_response = Response('http://test:12345',
                             body=mock_html_nolinks)
    mock_response.request = scrape_request
    mock_response.headers = html_headers
    mock_response.status = 200
    mock_response.encoding = u'ascii'
    mock_response.flags = []

    # Call the spider on the mock response
    pipeline_generator = spider.parse(mock_response)

    # Assert that we have two requests for this linkless page, one for each
    # of the user agents we inserted
    request_uas = []
    for new_request in pipeline_generator:
        if isinstance(new_request, Request):
            request_uas.append(new_request.meta['user_agent'])
        else:
            # We're not expecting anything other than Requests
            assert False

    assert set(request_uas) == set([u'Firefox / 11.0', u'Chrome / 20.0'])

def test_spider_crawls_links(spider, scrape_request, html_headers,
                           mock_html_twolinks):
    """Ensure spider always picks up relevant links to HTML pages"""
    # Use only 1 user agent for easier counting
    ua1 = model.UserAgent()
    ua1.ua_string = u'Firefox / 11.0'
    ua1.save()
    spider.user_agents = list(model.UserAgent.objects.all())

    # Generate a mock response based on html containing two links
    mock_response = Response('http://test:12345',
                             body=mock_html_twolinks)
    mock_response.request = scrape_request
    mock_response.headers = html_headers
    mock_response.status = 200
    mock_response.encoding = u'ascii'
    mock_response.flags = []

    # Call spider on the mock response
    pipeline_generator = spider.parse(mock_response)

    # Assert that we got the expected set of new requests generated in the
    # spider and nothing else
    sites_expected = set([mock_response.url,
                     mock_response.url + '/link1.html',
                     mock_response.url + '/link2.html'])
    sites_collected = []
    for new_request in pipeline_generator:
        if isinstance(new_request, Request):
            sites_collected.append(new_request.url)
        else:
            assert False

    assert sites_expected == set(sites_collected)

def test_savedcontent(spider, scrape_request, html_headers):
    """Ensure html, css, and javascript items are emitted correctly"""
    assert False
