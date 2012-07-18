"""
Tests for SiteScan model
"""
from django.db import IntegrityError
from hashlib import sha256
import pytest
from spade import model

from . import factories


def pytest_funcarg__sitescan(request):
    return factories.SiteScanFactory()


def test_unicode(sitescan):
    """Unicode representation of sitescan gives URL."""
    assert unicode(sitescan) == u"http://www.mozilla.com"


def test_constraint():
    """
    Ensure that two entries with the same page hash+site scan object cannot
    be inserted
    """
    sitescan = factories.SiteScanFactory.create(
        site_url_hash=sha256("http://www.mozilla.com").hexdigest(),
        site_url="http://www.mozilla.com")

    with pytest.raises(IntegrityError):
        model.SiteScan.objects.create(
            batch=sitescan.batch,
            site_url_hash=sha256("http://www.mozilla.com").hexdigest(),
            site_url="http://www.somethingdifferent.com")
