"""
Tests for Batch model
"""

from . import factories
from spade.model import models


def pytest_funcarg__batch(request):
    return factories.BatchFactory()


def test_unicode(batch):
    """Unicode representation of batch gives kickoff time."""
    assert unicode(batch) == (u"Batch started at 2012-06-29 ",
                              u"21:10:24.010848+00:00",)


def test_finish_time(batch):
    """Ensure that there is a datetime field finish_time"""
    assert format(batch.finish_time) == u"2012-06-29 21:10:24.010848+00:00"
