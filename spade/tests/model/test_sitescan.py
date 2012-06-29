"""
Tests for SiteScan model
"""
from datetime import datetime
from django.utils.timezone import utc
from spade.model.models import SiteScan, Batch

def test_unicode():
    """Unicode representation of sitescan gives URL."""
    mock_batch = Batch()
    mock_batch.kickoff_time = datetime.utcnow().replace(tzinfo=utc)
    mock_batch.finish_time = datetime.utcnow().replace(tzinfo=utc)
    mock_batch.save()

    sitescan = SiteScan()
    sitescan.batch = mock_batch
    sitescan.site_url = "http://www.google.com"
    sitescan.save()

    assert unicode(sitescan) == "http://www.google.com"
