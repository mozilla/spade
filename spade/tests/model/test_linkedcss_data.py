"""
Tests for linkedcss data model
"""

from . import factories


def test_unicode():
    """Unicode representation of linkedcss gives correct number of issues"""
    linkedcss = factories.LinkedCSSFactory.create()

    linkedcss_data = factories.LinkedCSSDataFactory.create(
        linked_css=linkedcss, css_issues=3)

    assert unicode(linkedcss_data) == u"'http://example.com/test.css' has (3) css issues"

