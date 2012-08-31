# Factories for testing objects
from datetime import datetime
from hashlib import sha256

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.timezone import utc
import factory

from spade.model import models

MOCK_DATE = datetime(2012, 6, 29, 21, 10, 24, 10848, tzinfo=utc)
MOCK_CSS_URL = u"http://example.com/test.css"
MOCK_JS_URL = u"http://example.com/test.js"


class BatchFactory(factory.Factory):
    """ Batch model factory """
    FACTORY_FOR = models.Batch
    kickoff_time = datetime.now(utc)
    finish_time = datetime.now(utc)


class BatchUserAgentFactory(factory.Factory):
    """ Batch user agent factory """
    FACTORY_FOR = models.BatchUserAgent
    batch = factory.SubFactory(BatchFactory)
    ua_string = "Firefox / 5.0"


class SiteScanFactory(factory.Factory):
    """ Site scan model factory """
    FACTORY_FOR = models.SiteScan
    batch = factory.SubFactory(BatchFactory)
    site_url = u"http://www.mozilla.com"
    site_url_hash = sha256(site_url).hexdigest()


class URLScanFactory(factory.Factory):
    """ URL scan model factory """
    FACTORY_FOR = models.URLScan
    site_scan = factory.SubFactory(SiteScanFactory)
    page_url = u"http://www.mozilla.com"
    timestamp = MOCK_DATE
    page_url_hash = sha256("http://www.mozilla.com").hexdigest()


class UserAgentFactory(factory.Factory):
    """ User agent model factory """
    FACTORY_FOR = models.UserAgent
    ua_string = u"Firefox / 5.0"


class URLContentFactory(factory.Factory):
    """ URL Content model factory """
    FACTORY_FOR = models.URLContent
    url_scan = factory.SubFactory(URLScanFactory)
    user_agent = factory.SubFactory(BatchUserAgentFactory)
    raw_markup = SimpleUploadedFile(
        "test.html", "<html>hello world</html>", "text/html")
    headers = u""


class LinkedCSSFactory(factory.Factory):
    """ Linked CSS model factory """
    FACTORY_FOR = models.LinkedCSS
    batch = factory.SubFactory(BatchFactory)
    url = MOCK_CSS_URL
    url_hash = sha256(MOCK_CSS_URL).hexdigest()
    raw_css = SimpleUploadedFile("test.css", "body{color:#000}", "text/css")


class LinkedJSFactory(factory.Factory):
    """ Linked JS model factory """
    FACTORY_FOR = models.LinkedJS
    batch = factory.SubFactory(BatchFactory)
    url = MOCK_JS_URL
    url_hash = sha256(MOCK_JS_URL).hexdigest()
    raw_js = SimpleUploadedFile(
        "test.js", "document.write('hello world')", "application/javascript")


class CSSRuleFactory(factory.Factory):
    """ CSS Rule model factory """
    FACTORY_FOR = models.CSSRule
    linkedcss = factory.SubFactory(LinkedCSSFactory)
    selector = "body"


class CSSPropertyFactory(factory.Factory):
    """ CSS Property model factory """
    FACTORY_FOR = models.CSSProperty
    rule = factory.SubFactory(CSSRuleFactory)
    prefix = ""
    name = "text-decoration"
    value = "none"


class BatchDataFactory(factory.Factory):
    """ Factory for batch data """
    FACTORY_FOR = models.BatchData
    batch = factory.SubFactory(BatchFactory)

    # Dummy metric numbers
    num_rules = 5
    num_properties = 10
    scanned_pages = 1
    css_issues = 3
    ua_issues = 1


class SiteScanDataFactory(factory.Factory):
    """ Factory for sitescan data """
    FACTORY_FOR = models.SiteScanData
    sitescan = factory.SubFactory(SiteScanFactory)

    # Dummy metric numbers
    num_rules = 5
    num_properties = 10
    scanned_pages = 1
    css_issues = 3
    ua_issues = 1


class URLScanDataFactory(factory.Factory):
    """ Factory for urlscan data """
    FACTORY_FOR = models.URLScanData
    urlscan = factory.SubFactory(URLScanFactory)

    # Dummy metric numbers
    num_rules = 5
    num_properties = 10
    css_issues = 3
    ua_issue = True


class URLContentDataFactory(factory.Factory):
    """ Factory for urlcontent data """
    FACTORY_FOR = models.URLContentData
    urlcontent = factory.SubFactory(URLContentFactory)

    # Dummy metric numbers
    num_rules = 3
    num_properties = 10
    css_issues = 3


class LinkedCSSDataFactory(factory.Factory):
    """ Factory for LinkedCSS data """
    FACTORY_FOR = models.LinkedCSSData
    linked_css = factory.SubFactory(LinkedCSSFactory)

    # Dummy metric numbers
    num_rules = 3
    num_properties = 10
    css_issues = 3
