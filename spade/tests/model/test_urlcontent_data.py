"""
Tests for urlcontent data model
"""

from . import factories


def test_unicode():
    """Unicode representation of urlcontent gives correct number of issues"""
    ua = factories.BatchUserAgentFactory.create(ua_string="Mozilla / 5.0")

    urlcontent = factories.URLContentFactory.create(user_agent=ua)

    urlcontent_data = factories.URLContentDataFactory.create(
        urlcontent=urlcontent, css_issues=3)

    assert unicode(urlcontent_data) == (u"'Page scanned with user agent "
                                        u"'Mozilla / 5.0' has (3) css issues")
