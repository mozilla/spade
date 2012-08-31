"""
Tests for data aggregation util
"""
from datetime import datetime
from django.utils.timezone import utc
from spade.model import models
from spade.tests.model import factories
from spade.utils.data_aggregator import DataAggregator

MOCK_DATE = datetime(2012, 6, 29, 21, 10, 24, 10848, tzinfo=utc)



def test_detect_ua_issue_single_desktop():
    """
    Given a urlscan hierarchy with different user agents, ensure we can
    detect UA sniffing problems. Setting: 1 desktop UA, 2 mobile UAs.
    """
    da = DataAggregator()
    urlscan = factories.URLScanFactory.create()

    batch = models.Batch.objects.create(kickoff_time=MOCK_DATE,
                                        finish_time=MOCK_DATE)

    # Set up the first UA, a desktop UA
    ua1 = models.BatchUserAgent.objects.create(batch=batch, ua_string="ua1",
        ua_type=models.BatchUserAgent.DESKTOP)
    markup_1 = u"<html>hello world</html>"
    models.URLContent.objects.create(url_scan=urlscan,
                                     user_agent=ua1,
                                     raw_markup=markup_1,
                                     headers=u"")

    # Set up the second UA, a mobile UA that is the "primary ua," the one we
    # want to ensure has been served new content
    ua2 = models.BatchUserAgent.objects.create(batch=batch, ua_string="ua2",
        ua_type=models.BatchUserAgent.MOBILE, primary_ua=True)
    markup_2 = u"<html>site structure didn't change</html>"
    models.URLContent.objects.create(url_scan=urlscan,
                                     user_agent=ua2,
                                     raw_markup=markup_2,
                                     headers=u"")

    # Set up a third UA, mobile. Make it have different content, so that it
    # supposedly will be detected to have been "sniffed"
    ua3 = models.BatchUserAgent.objects.create(batch=batch, ua_string="ua3",
        ua_type=models.BatchUserAgent.MOBILE)
    markup_3 = (u"<html><head><title></title><link href="" /></head>"
                u"<body><div>hello world</div></body></html>")
    models.URLContent.objects.create(url_scan=urlscan,
                                     user_agent=ua3,
                                     raw_markup=markup_3,
                                     headers=u"")

    assert da.detect_ua_issue(urlscan) == True

def test_detect_ua_issue_multiple_desktop():
    """
    Given a urlscan hierarchy with different user agents, ensure we can
    detect UA sniffing problems. Setting: 2 desktop UAs, 2 mobile UAs.
    """
    da = DataAggregator()
    urlscan = factories.URLScanFactory.create()

    batch = models.Batch.objects.create(kickoff_time=MOCK_DATE,
                                        finish_time=MOCK_DATE)

    # Set up the first UA, a desktop UA
    ua0 = models.BatchUserAgent.objects.create(batch=batch, ua_string="ua0",
        ua_type=models.BatchUserAgent.DESKTOP)
    markup_0 = u"<html>hello world</html>"
    models.URLContent.objects.create(url_scan=urlscan,
                                     user_agent=ua0,
                                     raw_markup=markup_0,
                                     headers=u"")

    # Set up the second UA, another desktop UA
    ua1 = models.BatchUserAgent.objects.create(batch=batch, ua_string="ua1",
        ua_type=models.BatchUserAgent.DESKTOP)
    markup_1 = u"<html><div>something different</div></html>"
    models.URLContent.objects.create(url_scan=urlscan,
                                     user_agent=ua1,
                                     raw_markup=markup_1,
                                     headers=u"")

    # Set up the third UA, a mobile UA that is the "primary ua," the one we
    # want to ensure has been served new content
    ua2 = models.BatchUserAgent.objects.create(batch=batch, ua_string="ua2",
        ua_type=models.BatchUserAgent.MOBILE, primary_ua=True)
    markup_2 = u"<html><div>site structure didn't change</div></html>"
    models.URLContent.objects.create(url_scan=urlscan,
                                     user_agent=ua2,
                                     raw_markup=markup_2,
                                     headers=u"")

    # Set up a fourth UA, mobile. Make it have different content, so that it
    # supposedly will be detected to have been "sniffed"
    ua3 = models.BatchUserAgent.objects.create(batch=batch, ua_string="ua3",
        ua_type=models.BatchUserAgent.MOBILE)
    markup_3 = (u"<html><head><title></title><link href="" /></head>"
                u"<body><div>hello world</div></body></html>")
    models.URLContent.objects.create(url_scan=urlscan,
                                     user_agent=ua3,
                                     raw_markup=markup_3,
                                     headers=u"")

    assert da.detect_ua_issue(urlscan) == True


def test_detect_no_ua_issue():
    """
    Given a urlscan hierarchy with different user agents, we should be able to
    tell when there aren't UA sniffing problems.
    """
    da = DataAggregator()
    urlscan = factories.URLScanFactory.create()

    batch = models.Batch.objects.create(kickoff_time=MOCK_DATE,
                                        finish_time=MOCK_DATE)

    # Set up the first UA, a desktop UA
    ua0 = models.BatchUserAgent.objects.create(batch=batch, ua_string="ua0",
        ua_type=models.BatchUserAgent.DESKTOP)
    markup_0 = u"<html>hello world</html>"
    models.URLContent.objects.create(url_scan=urlscan,
                                     user_agent=ua0,
                                     raw_markup=markup_0,
                                     headers=u"")

    # Set up the second UA, a desktop UA
    ua1 = models.BatchUserAgent.objects.create(batch=batch, ua_string="ua1",
        ua_type=models.BatchUserAgent.DESKTOP)
    markup_1 = u"<html><div>hello world</div></html>"
    models.URLContent.objects.create(url_scan=urlscan,
                                     user_agent=ua1,
                                     raw_markup=markup_1,
                                     headers=u"")

    # Set up the first mobile UA, the primary ua.
    ua2 = models.BatchUserAgent.objects.create(batch=batch, ua_string="ua2",
        ua_type=models.BatchUserAgent.MOBILE, primary_ua=True)
    markup_2 = (u"<html><head><title></title></head>"
                u"<body><div><div></div></div></body></html>")
    models.URLContent.objects.create(url_scan=urlscan,
                                     user_agent=ua2,
                                     raw_markup=markup_2,
                                     headers=u"")

    # Set up a third UA, mobile, different content, but sniffing detected
    ua3 = models.BatchUserAgent.objects.create(batch=batch, ua_string="ua3",
        ua_type=models.BatchUserAgent.MOBILE)
    markup_3 = (u"<html><head><title></title><link href="" /></head>"
                u"<body><div>hello world</div></body></html>")
    models.URLContent.objects.create(url_scan=urlscan,
                                     user_agent=ua3,
                                     raw_markup=markup_3,
                                     headers=u"")

    assert da.detect_ua_issue(urlscan) == False
