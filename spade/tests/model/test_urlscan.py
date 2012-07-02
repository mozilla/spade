"""
Test URLScan model
"""
from . import factories

def pytest_funcarg__urlscan(request):
    return factories.URLScanFactory()

def test_unicode(urlscan):
    assert unicode(urlscan) == u"http://www.mozilla.com"
