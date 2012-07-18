"""
Tests for SiteScan model
"""
from . import factories
from spade import model
from hashlib import sha256
from django.db import IntegrityError


def test_unicode():
    """Unicode representation of sitescan gives URL."""
    assert unicode(factories.SiteScanFactory()) == u"http://www.mozilla.com"


def teardown_function(function):
    model.SiteScan.objects.filter(site_url_hash=sha256("http://www.mozilla.com").hexdigest()).delete()


def test_constraint():
    """
    Ensure that two entries with the same page hash+site scan object cannot
    be inserted
    """
    test_batch = factories.BatchFactory()
    ss_created = model.SiteScan.objects.create(
        batch=test_batch,
        site_url_hash=sha256("http://www.mozilla.com").hexdigest(),
        site_url="http://www.somethingdifferent.com")

    try:
        ss_created = model.SiteScan.objects.create(
            batch=test_batch,
            site_url_hash=sha256("http://www.mozilla.com").hexdigest(),
            site_url="http://www.somethingdifferent.com")
        assert False

    except IntegrityError:
        assert True
