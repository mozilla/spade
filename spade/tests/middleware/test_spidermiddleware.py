from scrapy.conf import settings

from spade.scraper.middlewares import CustomDepthMiddleware
from spade.scraper.middlewares import CustomOffsiteMiddleware


def pytest_funcarg__offsitemiddleware(request):
    return ""


def pytest_funcarg__depthmiddleware(request):
    return ""


def test_offsitefilter(offsitemiddleware):
    """Ensure offsite links are not crawled"""
    # This needs to test the offsitemiddleware (a spidermiddleware) which sends
    # requests to the scheduler. Enure that requests emitted do not go offsite.
    assert False


def test_crawl_1level(depthmiddleware):
    """Ensure we only download 1 level of html"""
    # This test needs to insert a request into the downloader middleware and
    # ensure that no response comes out of the downloader
    assert False


def test_crawl_linked_morelevels(depthmiddleware):
    """Ensure all CSS/JS is downloaded on crawled html pages"""
    # This test needs to insert a request into the downloader middleware and
    # ensure that a valid response comes out
    assert False
