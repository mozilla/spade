"""Tests for custom dupefilter."""
from scrapy.http.request import Request

from spade.scraper.dupefilter import MultipleUADupeFilter


def pytest_funcarg__df(request):
    """Give a test access to a MultipleUADupeFilter instance."""
    return MultipleUADupeFilter()



def test_filters_dupes(df):
    """Dupefilter returns True for an already-seen URL."""
    r1 = Request("http://example.com")
    r2 = Request("http://example.com")

    assert not df.request_seen(r1)
    assert df.request_seen(r2)



def test_filters_same_ua_dupes(df):
    """Dupefilter returns True for an already-seen URL with same UA."""
    r1 = Request("http://example.com", headers={"User-Agent": "Mozilla/5.0"})
    r2 = Request("http://example.com", headers={"User-Agent": "Mozilla/5.0"})

    assert not df.request_seen(r1)
    assert df.request_seen(r2)



def test_does_not_filter_different_ua_dupes(df):
    """Dupefilter returns False for an already-seen URL with different UA."""
    r1 = Request("http://example.com", headers={"User-Agent": "Mozilla/5.0"})
    r2 = Request("http://example.com", headers={"User-Agent": "IE/10.0"})

    assert not df.request_seen(r1)
    assert not df.request_seen(r2)
