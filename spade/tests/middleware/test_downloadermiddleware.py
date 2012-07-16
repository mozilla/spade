from scrapy.conf import settings

def pytest_funcarg__downloadermiddleware(request):
    return ""

def test_crawl_1level(downloadermiddleware):
    """Ensure we only download 1 level of html"""
    # This test needs to insert a request into the downloader middleware and
    # ensure that no response comes out of the downloader
    assert False

def test_crawl_linked_morelevels(downloadermiddleware):
    """Ensure all CSS/JS is downloaded on crawled html pages"""
    # This test needs to insert a request into the downloader middleware and
    # ensure that a valid response comes out
    assert False
