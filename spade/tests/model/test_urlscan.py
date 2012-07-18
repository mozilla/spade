"""
Test URLScan model
"""
import pytest

from . import factories
from datetime import datetime
from django.db import IntegrityError
from django.utils.timezone import utc
from hashlib import sha256
from spade import model

MOCK_DATE = datetime(2012, 6, 29, 21, 10, 24, 10848, tzinfo=utc)


def test_unicode():
    urlscan = factories.URLScanFactory.create()
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
