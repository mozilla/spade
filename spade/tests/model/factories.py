# Factories for testing objects
import factory

from datetime import datetime
from django.utils.timezone import utc
from hashlib import sha256
from spade.model import models

MOCK_DATE = datetime(2012, 6, 29, 21, 10, 24, 10848, tzinfo=utc)
MOCK_CSS_URL = (u"http://www.sammyliu.com/wp-content/themes/polaroid-perfect/",
                u"style.css",)
MOCK_JS_URL = u"http://code.jquery.com/jquery-1.7.2.min.js"


class BatchFactory(factory.Factory):
    """Batch model factory"""
    FACTORY_FOR = models.Batch
    kickoff_time = MOCK_DATE
    finish_time = MOCK_DATE


class SiteScanFactory(factory.Factory):
    """Site scan model factory"""
    FACTORY_FOR = models.SiteScan
    batch = factory.SubFactory(BatchFactory)
    site_url = u"http://www.mozilla.com"


class URLScanFactory(factory.Factory):
    """URL scan model factory"""
    FACTORY_FOR = models.URLScan
    site_scan = factory.SubFactory(SiteScanFactory)
    page_url = u"http://www.mozilla.com"
    timestamp = MOCK_DATE
    page_url_hash = sha256("http://www.mozilla.com")


class UserAgentFactory(factory.Factory):
    """User agent model factory"""
    FACTORY_FOR = models.UserAgent
    ua_string = u"Firefox / 5.0"


class URLContentFactory(factory.Factory):
    """URL Content model factory"""
    FACTORY_FOR = models.URLContent
    url_scan = factory.SubFactory(URLScanFactory)
    user_agent = u"Firefox / 5.0"
    raw_markup = u"<html>hello world</html>"
    headers = u""


class LinkedCSSFactory(factory.Factory):
    """Linked CSS model factory"""
    FACTORY_FOR = models.LinkedCSS
    url = MOCK_CSS_URL
    url_hash = sha256(MOCK_CSS_URL)
    raw_css = u"body{color:#000}"


class LinkedJSFactory(factory.Factory):
    """Linked JS model factory"""
    FACTORY_FOR = models.LinkedJS
    url = MOCK_JS_URL
    url_hash = sha256(MOCK_JS_URL)
    raw_js = u"document.write('hello world')"
