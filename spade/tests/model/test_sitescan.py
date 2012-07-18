"""
Tests for SiteScan model
"""
from . import factories
from spade import model
from hashlib import sha256
from django.db import IntegrityError


def pytest_funcarg__sitescan(request):
    return factories.SiteScanFactory()


def test_unicode(sitescan):
    """Unicode representation of sitescan gives URL."""
    assert unicode(sitescan) == u"http://www.mozilla.com"


def test_constraint(sitescan):
    """
    Ensure that two entries with the same page hash+site scan object cannot
    be inserted
    """
    ss_created = model.SiteScan.objects.create(
        batch=sitescan.batch,
        site_url_hash=sha256("http://www.mozilla.com").hexdigest(),
        site_url="http://www.mozilla.com")

    try:
        ss_created = model.SiteScan.objects.create(
            batch=sitescan.batch,
            site_url_hash=sha256("http://www.mozilla.com").hexdigest(),
            site_url="http://www.somethingdifferent.com")
        assert False

    except IntegrityError:
        assert True
