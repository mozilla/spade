"""
Tests for urlscan data model
"""

from . import factories


def test_unicode():
    """Unicode representation of urlscan gives correct numbers of issues."""
    urlscan = factories.URLScanFactory.create()

    urlscan_data = factories.URLScanDataFactory.create(urlscan=urlscan,
                                                       css_issues=3,
                                                       ua_issue=True)

    assert unicode(urlscan_data) == (
        u"'http://www.mozilla.com' has (3) css issues")
