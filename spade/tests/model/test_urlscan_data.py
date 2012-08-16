"""
Tests for urlscan data model
"""

from . import factories


def test_unicode():
    """Unicode representation of urlscan gives correct numbers of issues."""
    urlscan = factories.URLScanFactory.create()

    urlscan_data = factories.URLScanDataFactory.create(urlscan=urlscan,
                                                         css_issues=3,
                                                         ua_issues=4)

    assert unicode(urlscan_data) == (u"'URL scanned has (3) css issues and (4) "
                                     u"ua issues")
