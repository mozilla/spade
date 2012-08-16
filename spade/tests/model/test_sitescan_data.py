"""
Tests for site scan data model
"""

from . import factories


def test_unicode():
    """Unicode representation of site scan gives correct numbers of issues."""
    sitescan = factories.SiteScanFactory.create()

    sitescan_data = factories.SiteScanDataFactory.create(sitescan=sitescan,
                                                         css_issues=3,
                                                         ua_issues=4)

    assert unicode(sitescan_data) == (u"'Site scanned has (3) css issues and"
                                     u" (4) ua issues")
