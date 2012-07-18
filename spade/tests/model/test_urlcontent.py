"""
Tests for URLContent model
"""
from . import factories


def pytest_funcarg__urlcontent(request):
    return factories.URLContentFactory()


def test_unicode(urlcontent):
    print "sup"
    default_string = u"'http://www.mozilla.com' scanned with 'Firefox / 5.0'"
    assert unicode(urlcontent) == default_string
