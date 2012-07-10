from scrapy.conf import settings

def pytest_funcarg__spidermiddleware(request):
    return ""

def test_offsitefilter(spidermiddleware):
    """Ensure offsite links are not crawled"""
    # This needs to test the offsitemiddleware (a spidermiddleware) which sends
    # requests to the scheduler. Enure that requests emitted do not go offsite.
    assert False
