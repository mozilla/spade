"""
Tests for Batch model
"""

from . import factories
from datetime import datetime
from django.utils.timezone import utc

MOCK_DATE = datetime(2012, 6, 29, 21, 10, 24, 10848, tzinfo=utc)


def test_unicode():
    """Unicode representation of batch gives kickoff time."""
    batch = factories.BatchFactory.create(
        kickoff_time=MOCK_DATE, finish_time=MOCK_DATE)
    assert unicode(batch) == (u"Batch started at 2012-06-29 "
                              u"21:10:24.010848+00:00")


def test_finish_time():
    """Ensure that there is a datetime field finish_time"""
    batch = factories.BatchFactory.create(
        kickoff_time=MOCK_DATE, finish_time=MOCK_DATE)
    assert format(batch.finish_time) == u"2012-06-29 21:10:24.010848+00:00"
