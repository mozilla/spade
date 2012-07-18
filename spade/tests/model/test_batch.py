"""
Tests for Batch model
"""

from . import factories
from datetime import datetime
from django.utils.timezone import utc
from spade.model import models

MOCK_DATE = datetime(2012, 6, 29, 21, 10, 24, 10848, tzinfo=utc)


def pytest_funcarg__batch(request):
    batch = factories.BatchFactory.build()
    batch.kickoff_time = MOCK_DATE
    batch.finish_time = MOCK_DATE
    batch.save()

    return batch


def test_unicode(batch):
    """Unicode representation of batch gives kickoff time."""
    assert unicode(batch) == (u"Batch started at 2012-06-29 "
                              u"21:10:24.010848+00:00")


def test_finish_time(batch):
    """Ensure that there is a datetime field finish_time"""
    assert format(batch.finish_time) == u"2012-06-29 21:10:24.010848+00:00"
