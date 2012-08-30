"""
Spade models.

"""
from datetime import datetime
from django.db import models


# The following organizes a naming scheme for local filesystem
# Takes a urlcontent instance and a filename
def get_file_path_components(instance, filename):
    now = datetime.now()
    return [unicode(now.year), unicode(now.month), unicode(now.day),
            unicode(now.hour), unicode(now.minute), filename]


# Define file naming callables
def html_filename(instance, filename):
    return '/'.join(
        ['html'] + get_file_path_components(
            instance, filename or "index.html"))


def css_filename(instance, filename):
    return '/'.join(['css'] + get_file_path_components(instance, filename))


def headers_filename(instance, filename):
    return '/'.join(
        ['headers'] + get_file_path_components(instance, filename or "index"))


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


class BatchUserAgent(models.Model):
    """ A user agent from a given batch """
    batch = models.ForeignKey(Batch)
    ua_string = models.CharField(max_length=250)

    def __unicode__(self):
        return self.ua_string

    class Meta:
        unique_together = [("batch", "ua_string")]


class SiteScan(models.Model):
    """An individual site scanned."""
    batch = models.ForeignKey(Batch, db_index=True)
    site_url = models.TextField()

    # Need the hash of the URL to be in a key constraint. A "Textfield" cannot
    # be in a key constraint. Thus we have both fields for the site_url as well
    # as a hash of the url, which we ultimately use in the (batch, url_hash)
    # key constraint.
    site_url_hash = models.CharField(max_length=64)

    def __unicode__(self):
        return self.site_url

    class Meta:
        unique_together = ("batch", "site_url_hash")


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

    def __unicode__(self):
        return self.page_url

    class Meta:
        unique_together = ("site_scan", "page_url_hash")


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
    user_agent = models.ForeignKey(BatchUserAgent)
    raw_markup = models.FileField(
        max_length=500, upload_to=html_filename)
    headers = models.FileField(
        max_length=500, upload_to=headers_filename)

    def __unicode__(self):
        return u"'{0}' scanned with '{1}'".format(
            self.url_scan, self.user_agent.ua_string)


class LinkedCSS(models.Model):
    """A single linked CSS file."""
    batch = models.ForeignKey(Batch)
    linked_from = models.ManyToManyField(URLContent)
    url = models.TextField()
    url_hash = models.CharField(max_length=64)
    raw_css = models.FileField(
        max_length=500, upload_to=css_filename)

    def __unicode__(self):
        return self.raw_css.name

    class Meta:
        verbose_name_plural = "Linked CSS"


class LinkedJS(models.Model):
    """A single linked JS file."""
    batch = models.ForeignKey(Batch)
    linked_from = models.ManyToManyField(URLContent)
    url = models.TextField()
    url_hash = models.CharField(max_length=64)
    raw_js = models.FileField(
        max_length=500, upload_to=js_filename)

    def __unicode__(self):
        return self.raw_js.name

    class Meta:
        verbose_name_plural = "Linked JS"


class CSSRule(models.Model):
    """A CSS element rule"""
    linkedcss = models.ForeignKey(LinkedCSS)
    selector = models.CharField(max_length=50)


class CSSProperty(models.Model):
    """A CSS property belonging to a rule"""
    rule = models.ForeignKey(CSSRule)
    prefix = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
