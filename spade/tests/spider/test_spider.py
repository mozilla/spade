from scrapy.conf import settings
from spade.scraper.spiders.general_spider import GeneralSpider
from spade.tests.spider.webserver.server import TestServer

def pytest_funcarg__spider(request):
    """Use scrapy's overrides to start the spider w/ specific settings"""
    settings.overrides['LOG_ENABLED'] = True
    settings.overrides['URLS'] = "spade/tests/sitelists/urls.txt"
    spider = GeneralSpider()
    spider.user_agents = ['Firefox / 13.0', 'Chrome / 11.0']

    return spider

def pytest_funcarg__server(request):
    """Mock web server with some pages we can test"""
    server = TestServer(8181)
    server.startserver()
    return server

def test_name(spider):
    """Ensure the spider's name is correct"""
    assert spider.name == "all"

def test_read_from_file(spider):
    """Ensure the test list of urls was read correctly"""
    if len(start_urls) != 1:
        assert False
    elif start_urls[0] == "http://localhost:8181":
        assert True
    else:
        assert False

def test_crawl_site(spider):
    """Ensure crawl gets kicked off and ends without failure"""
    # STUB
    assert False

def test_crawl_1level(spider, server):
    """Ensure crawl only descends to 1 level"""
    # STUB
    server.
    assert False

def test_useragents(spider, server):
    """Ensure multiple items with different user agent strings are emitted"""
    assert False

def test_savedcontent(spider, server):
    """Ensure html, css, and javascript are saved correctly"""
    assert False

def test_offsitefilter(spider, server):
    """Ensure offsite links are not crawled"""
    assert False

def test_duplinks(spider, server):
    """Ensure pages containing two of the same link only visit once / save 1"""
    assert False
