"""
Test URLScan model
"""
from datetime import datetime
from django.db import IntegrityError
from django.utils.timezone import utc
from hashlib import sha256
import pytest
from spade import model

from . import factories



MOCK_DATE = datetime(2012, 6, 29, 21, 10, 24, 10848, tzinfo=utc)

def pytest_funcarg__urlscan(request):
    return factories.URLScanFactory.create()


def test_unicode(urlscan):
    assert unicode(urlscan) == u"http://www.mozilla.com"


def test_constraint():
    """
    Ensure that two entries with the same page hash+site scan object cannot
    be inserted
    """
    urlscan = factories.URLScanFactory.create(
        page_url_hash=sha256(u"http://www.mozilla.com").hexdigest(),
        page_url=u"http://www.mozilla.com",
        timestamp=MOCK_DATE)

    with pytest.raises(IntegrityError):
        model.URLScan.objects.create(
            site_scan=urlscan.site_scan,
            page_url_hash=sha256(u"http://www.mozilla.com").hexdigest(),
            page_url=u"http://www.irrelevant.com",
            timestamp=datetime.now(tz=utc))
