"""
Tests for Batch Data model
"""

from . import factories
from datetime import datetime
from django.utils.timezone import utc

MOCK_DATE = datetime(2012, 6, 29, 21, 10, 24, 10848, tzinfo=utc)


def test_unicode():
    """Unicode representation of batch gives kickoff time."""
    batch = factories.BatchFactory.create(
        kickoff_time=MOCK_DATE, finish_time=MOCK_DATE)

    batchdata = factories.BatchDataFactory.create(
        batch=batch, num_rules=1, num_properties=2, css_issues=3, ua_issues=4)

    assert unicode(batchdata) == u"''Batch started at 2012-06-29 21:10:24.010848+00:00' has (3) css issues and (4) ua issues"
