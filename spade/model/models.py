"""
Spade models.

"""
from datetime import datetime
from django.db import models
from urlparse import urlparse

# The following organizes a naming scheme for local filesystem
def get_file_path_components(instance, filename):
    now = datetime.now()
    return [unicode(now.year), unicode(now.month), unicode(now.day),
            urlparse(instance.url_scan.site_scan.site_url).netloc, filename]

# Define file naming callables
def html_filename(instance, filename):
    filename = filename or "index.html"
    return '/'.join(['html'] +
                  get_file_path_components(instance, filename or "index.html"))

def css_filename(instance, filename):
    return '/'.join(['css'] + get_file_path_components(instance, filename))

def headers_filename(instance, filename):
    return '/'.join(['headers'] + get_file_path_components(instance, filename))

def js_filename(instance, filename):
    return '/'.join(['js'] + get_file_path_components(instance, filename))


class Batch(models.Model):
    """A batch of sites scanned in one run."""
    kickoff_time = models.DateTimeField("When crawl started")
    finish_time = models.DateTimeField("When crawl ended")

    def __unicode__(self):
        return u"Batch started at {0}".format(self.kickoff_time)

    class Meta:
        verbose_name_plural = u"Batches"


class SiteScan(models.Model):
    """An individual site scanned."""
    batch = models.ForeignKey(Batch, db_index=True)
    site_url = models.TextField()

    # Need the hash of the URL to be in a key constraint. A "Textfield" cannot
    # be in a key constraint. Thus we have both fields for the site_url as well
    # as a hash of the url, which we ultimately use in the (batch, url_hash)
    # key constraint.
    site_url_hash = models.CharField(max_length=64)


    class Meta:
        unique_together = ("batch", "site_url_hash")

    def __unicode__(self):
        return self.site_url


class URLScan(models.Model):
    """
    An individual URL scanned.

    For each ``SiteScan``, we follow links one level deep from the entry page,
    so every ``SiteScan`` will have a number of associated ``URLScan``s, one
    for the entry page URL and one for each link followed.
    """

    site_scan = models.ForeignKey(SiteScan, db_index=True)
    page_url = models.TextField()
    timestamp = models.DateTimeField("timestamp")

    # See comment for site_url_hash -- same reason.
    page_url_hash = models.CharField(max_length=64)

    class Meta:
        unique_together = ("site_scan", "page_url_hash")

    def __unicode__(self):
        return self.page_url


class UserAgent(models.Model):
    """A user-agent string we will use for scanning."""
    ua_string = models.CharField(max_length=250, unique=True)

    def __unicode__(self):
        return self.ua_string


class URLContent(models.Model):
    """
    The content for a particular user-agent from one scanned URL.

    Stores raw markup and headers; linked CSS and JS are stored in the
    ``LinkedCSS`` and ``LinkedJS`` tables.

    """
    url_scan = models.ForeignKey(URLScan)
    user_agent = models.CharField(max_length=250, db_index=True)
    raw_markup = models.FileField(
        max_length=500, upload_to=html_filename)
    headers = models.FileField(
        max_length=500, upload_to=headers_filename)

    def __unicode__(self):
        return u"'{0}' scanned with '{1}'".format(
            self.url_scan, self.user_agent)


class LinkedCSS(models.Model):
    """A single linked CSS file."""
    url_scan = models.ForeignKey(URLScan)
    raw_css = models.FileField(
        max_length=500, upload_to=css_filename)

    def __unicode__(self):
        return self.raw_css.name

    class Meta:
        verbose_name_plural = "Linked CSS"


class LinkedJS(models.Model):
    """A single linked JS file."""
    url_scan = models.ForeignKey(URLScan)
    raw_js = models.FileField(
        max_length=500, upload_to=js_filename)

    def __unicode__(self):
        return self.raw_js.name

    class Meta:
        verbose_name_plural = "Linked JS"
