"""
Spade models.

"""
from django.db import models


class Batch(models.Model):
    """A batch of sites scanned in one run."""
    kickoff_time    = models.DateTimeField("When crawl started")
    finish_time     = models.DateTimeField("When crawl ended")


class SiteScan(models.Model):
    """An individual site scanned."""
    batch       = models.ForeignKey(Batch, db_index=True)
    site_url    = models.CharField(max_length=200)


class URLScan(models.Model):
    """
    An individual URL scanned.

    For each ``SiteScan``, we follow links one level deep from the entry page,
    so every ``SiteScan`` will have a number of associated ``URLScan``s, one
    for the entry page URL and one for each link followed.

    """
    site_scan   = models.ForeignKey(SiteScan, db_index=True)
    page_url    = models.CharField(max_length=200)
    timestamp   = models.DateTimeField("timestamp")


class UserAgent(models.Model):
    """A user-agent string we will use for scanning."""
    ua_string   = models.CharField(max_length=250, unique=True)


class URLContent(models.Model):
    """
    The content for a particular user-agent from one scanned URL.

    Stores raw markup and headers; linked CSS and JS are stored in the
    ``LinkedCSS`` and ``LinkedJS`` tables.

    """
    url_scan    = models.ForeignKey(URLScan)
    user_agent  = models.CharField(max_length=250, db_index=True)
    raw_markup  = models.FileField(
        max_length=500, upload_to='crawls/html/%Y/%m/%d')
    headers     = models.FileField(
        max_length=500, upload_to='crawls/headers/%Y/%m/%d')


class LinkedCSS(models.Model):
    """A single linked CSS file."""
    url_scan = models.ForeignKey(URLScan)
    raw_css  = models.FileField(
        max_length=500, upload_to='crawls/css/%Y/%m/%d')


class LinkedJS(models.Model):
    """A single linked JS file."""
    url_scan = models.ForeignKey(URLScan)
    raw_js   = models.FileField(
        max_length=500, upload_to='crawls/js/%Y/%m/%d')


class CrawlList(models.Model):
    """A site URL to be crawled."""
    url = models.CharField(max_length=200, unique=True)
