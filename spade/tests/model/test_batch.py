"""
Tests for Batch model
"""
from datetime import datetime
from django.utils.timezone import utc
from spade.model.models import Batch

def test_unicode():
    """Unicode representation of batch gives kickoff time."""
    batch = Batch()
    mock_date = datetime(2012, 6, 29, 21, 10, 24, 10848, tzinfo=utc)
    batch.kickoff_time = mock_date
    batch.finish_time = mock_date
    batch.save()

    assert unicode(batch) == u"Batch started at 2012-06-29 21:10:24.010848+00:00"

def test_finish_time():
    """Ensure that there is a datetime field finish_time"""
    batch = Batch()
    mock_date = datetime(2012, 6, 29, 21, 10, 24, 10848, tzinfo=utc)
    batch.kickoff_time = mock_date
    batch.finish_time = mock_date
    batch.save()

    assert format(batch.finish_time) == "2012-06-29 21:10:24.010848+00:00"
