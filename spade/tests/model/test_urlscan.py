"""
Test URLScan model
"""
from . import factories
from datetime import datetime
from django.utils.timezone import utc
from hashlib import sha256
from spade import model
from django.db import IntegrityError

MOCK_DATE = datetime(2012, 6, 29, 21, 10, 24, 10848, tzinfo=utc)

def pytest_funcarg__urlscan(request):
    return factories.URLScanFactory.create()


def test_unicode(urlscan):
    assert unicode(urlscan) == u"http://www.mozilla.com"


def test_constraint(urlscan):
    """
    Ensure that two entries with the same page hash+site scan object cannot
    be inserted
    """
    us_created = model.URLScan.objects.create(
        site_scan=urlscan.site_scan,
        page_url_hash=sha256(u"http://www.mozilla.com").hexdigest(),
        page_url=u"http://www.mozilla.com",
        timestamp=MOCK_DATE)

    assert us_created

    try:
        us_created = model.URLScan.objects.create(
            site_scan=urlscan.site_scan,
            page_url_hash=sha256(u"http://www.mozilla.com").hexdigest(),
            page_url=u"http://www.irrelevant.com",
            timestamp=datetime.now(tz=utc))
        assert False

    except IntegrityError:
        assert True
