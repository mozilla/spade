# Factories for testing objects
import factory

from datetime import datetime
from django.utils.timezone import utc
from spade.model import models

MOCK_DATE = datetime(2012, 6, 29, 21, 10, 24, 10848, tzinfo=utc)

class BatchFactory(factory.Factory):
    FACTORY_FOR = models.Batch

    kickoff_time = MOCK_DATE
    finish_time = MOCK_DATE

class SiteScanFactory(factory.Factory):
    FACTORY_FOR = models.SiteScan

    batch = factory.SubFactory(BatchFactory)
    site_url = u"http://www.mozilla.com"

class URLScanFactory(factory.Factory):
    FACTORY_FOR = models.URLScan

    site_scan = factory.SubFactory(SiteScanFactory)
    page_url = u"http://www.mozilla.com"
    timestamp = MOCK_DATE

class UserAgentFactory(factory.Factory):
    FACTORY_FOR = models.UserAgent

    ua_string = u"Firefox / 5.0"

class URLContentFactory(factory.Factory):
    FACTORY_FOR = models.URLContent

    url_scan = factory.SubFactory(URLScanFactory)
    user_agent = u"Firefox / 5.0"
    raw_markup = u"<html>hello world</html>"
    headers = u""

class LinkedCSSFactory(factory.Factory):
    FACTORY_FOR = models.LinkedCSS

    url_scan = factory.SubFactory(URLScanFactory)
    raw_css = u"body{color:#000}"

class LinkedJSFactory(factory.Factory):
    FACTORY_FOR = models.LinkedJS

    url_scan = factory.SubFactory(URLScanFactory)
    raw_js = u"document.write('hello world')"
