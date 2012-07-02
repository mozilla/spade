"""
Spade models.

"""
from datetime import datetime
from django.db import models

# The following organizes a naming scheme for local filesystem
now = datetime.now()
YEAR = unicode(now.year)
MONTH = unicode(now.month)
DAY = unicode(now.day)

# Define file naming callables
def html_filename(instance, filename):
    fs = [YEAR, MONTH, DAY, instance.url_scan.site_scan.folder_name, filename]
    return '/'.join(['html']+fs)

def css_filename(instance, filename):
    fs = [YEAR, MONTH, DAY, instance.url_scan.site_scan.folder_name, filename]
    return '/'.join(['css']+fs)

def headers_filename(instance, filename):
    fs = [YEAR, MONTH, DAY, instance.url_scan.site_scan.folder_name, filename]
    return '/'.join(['headers']+fs)

def js_filename(instance, filename):
    fs = [YEAR, MONTH, DAY, instance.url_scan.site_scan.folder_name, filename]
    return '/'.join(['js']+fs)


class Batch(models.Model):
    """A batch of sites scanned in one run."""
    kickoff_time    = models.DateTimeField("When crawl started")
    finish_time     = models.DateTimeField("When crawl ended")

    def __unicode__(self):
        return u"Batch started at {0}".format(self.kickoff_time)

    class Meta:
        verbose_name_plural = u"Batches"


class SiteScan(models.Model):
    """An individual site scanned."""
    batch       = models.ForeignKey(Batch, db_index=True)
    site_url    = models.TextField()
    folder_name = models.TextField(max_length=200)

    def __unicode__(self):
        return self.site_url


class URLScan(models.Model):
    """
    An individual URL scanned.

    For each ``SiteScan``, we follow links one level deep from the entry page,
    so every ``SiteScan`` will have a number of associated ``URLScan``s, one
    for the entry page URL and one for each link followed.

    The folder_name is what the folder on disk will be called.

    """
    site_scan   = models.ForeignKey(SiteScan, db_index=True)
    page_url    = models.TextField()
    timestamp   = models.DateTimeField("timestamp")

    def __unicode__(self):
        return self.page_url


class UserAgent(models.Model):
    """A user-agent string we will use for scanning."""
    ua_string   = models.CharField(max_length=250, unique=True)

    def __unicode__(self):
        return self.ua_string


class URLContent(models.Model):
    """
    The content for a particular user-agent from one scanned URL.

    Stores raw markup and headers; linked CSS and JS are stored in the
    ``LinkedCSS`` and ``LinkedJS`` tables.

    """
    url_scan    = models.ForeignKey(URLScan)
    user_agent  = models.CharField(max_length=250, db_index=True)
    raw_markup  = models.FileField(
        max_length=500, upload_to=html_filename)
    headers     = models.FileField(
        max_length=500, upload_to=headers_filename)

    def __unicode__(self):
        return u"'{0}' scanned with '{1}'".format(
            self.url_scan, self.user_agent)


class LinkedCSS(models.Model):
    """A single linked CSS file."""
    url_scan = models.ForeignKey(URLScan)
    raw_css  = models.FileField(
        max_length=500, upload_to=css_filename)

    def __unicode__(self):
        return self.raw_css.name

    class Meta:
        verbose_name_plural = "Linked CSS"


class LinkedJS(models.Model):
    """A single linked JS file."""
    url_scan = models.ForeignKey(URLScan)
    raw_js   = models.FileField(
        max_length=500, upload_to=js_filename)

    def __unicode__(self):
        return self.raw_js.name

    class Meta:
        verbose_name_plural = "Linked JS"
