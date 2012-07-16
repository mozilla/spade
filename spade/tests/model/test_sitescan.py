"""
Tests for SiteScan model
"""
from datetime import datetime
from django.utils.timezone import utc
from spade.model.models import SiteScan, Batch


def pytest_funcarg__sitescan(request):
    batch = Batch()
    mock_date = datetime(2012, 6, 29, 21, 10, 24, 10848, tzinfo=utc)
    batch.kickoff_time = mock_date
    batch.finish_time = mock_date
    batch.save()

    sitescan = SiteScan()
    sitescan.batch = batch
    sitescan.site_url = "http://www.google.com"
    sitescan.save()
    return sitescan


def test_unicode(sitescan):
    """Unicode representation of sitescan gives URL."""

    assert unicode(sitescan) == "http://www.google.com"
