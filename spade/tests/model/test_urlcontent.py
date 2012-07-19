"""
Tests for URLContent model
"""
from . import factories


def test_unicode():
    urlcontent = factories.URLContentFactory()
    default_string = u"'http://www.mozilla.com' scanned with 'Firefox / 5.0'"
    assert unicode(urlcontent) == default_string
