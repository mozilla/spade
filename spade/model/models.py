"""
Spade models.

"""
from datetime import datetime
from django.db import models
from urlparse import urlparse


""" Naming scheme for local filesystem """

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


""" Models for scraper """


class UserAgent(models.Model):
    """ A user-agent string we will use for scanning. """
    DESKTOP = 0
    MOBILE = 1
    UA_TYPE_CHOICES = (
        (DESKTOP, 'desktop'),
        (MOBILE, 'mobile'),
    )

    ua_string = models.CharField(max_length=250, unique=True)
    ua_type = models.IntegerField(max_length=1,
                                  choices=UA_TYPE_CHOICES,
                                  default=DESKTOP)
    primary_ua = models.BooleanField(default=False)

    def __unicode__(self):
        return self.ua_string


class Batch(models.Model):
    """ A batch of sites scanned in one run. """
    kickoff_time = models.DateTimeField("When crawl started")
    finish_time = models.DateTimeField("When crawl ended")

    # Flag to see if this particular batch's data has yet been aggregated. This
    # gets set to true at the end of the aggregation step. That way if the
    # aggregation step was interrupted this will still be false and the data
    # models will be regenerated at the next run of the aggregation function
    data_aggregated = models.BooleanField(default=False)

    def __unicode__(self):
        return u"Batch started at {0}".format(self.kickoff_time)

    class Meta:
        verbose_name_plural = u"Batches"


class BatchUserAgent(models.Model):
    """ A user agent from a given batch """
    batch = models.ForeignKey(Batch, db_index=True)

    # The following clones the UserAgent model, so that we can retain history
    # for scan UAs while allowing the user to add/remove/modify user agents
    DESKTOP = 0
    MOBILE = 1
    UA_TYPE_CHOICES = (
        (DESKTOP, 'desktop'),
        (MOBILE, 'mobile'),
    )

    ua_string = models.CharField(max_length=250, unique=True)
    ua_type = models.IntegerField(max_length=1,
                                  choices=UA_TYPE_CHOICES,
                                  default=DESKTOP)
    primary_ua = models.BooleanField(default=False)

    def __unicode__(self):
        return self.ua_string


class SiteScan(models.Model):
    """ An individual site scanned. """
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
    """ A single linked CSS file. """
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
    """ A single linked JS file. """
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
    """ A CSS element rule """
    linkedcss = models.ForeignKey(LinkedCSS)
    selector = models.CharField(max_length=50)


class CSSProperty(models.Model):
    """ A CSS property belonging to a rule """
    rule = models.ForeignKey(CSSRule)
    prefix = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50)


""" Aggregate Data Models """


class BatchData(models.Model):
    """ Aggregate data model for scan batches """
    batch = models.OneToOneField(Batch)

    # Other metrics
    num_rules = models.IntegerField(max_length=50)
    num_properties = models.IntegerField(max_length=50)
    scanned_pages = models.IntegerField(max_length=50)

    # Aggregate number of css issues from all scans in all user agents
    css_issues = models.IntegerField(max_length=50)

    # Aggregate number of UA issues in this batch
    ua_issues = models.IntegerField(max_length=50)

    def __unicode__(self):
        return u"'Scan batch has ({0}) css issues and ({1}) ua issues".format(self.css_issues, self.ua_issues)


class SiteScanData(models.Model):
    """ Aggregate data model for site scans """
    sitescan = models.OneToOneField(SiteScan)

    # Other metrics
    num_rules = models.IntegerField(max_length=50)
    num_properties = models.IntegerField(max_length=50)
    scanned_pages = models.IntegerField(max_length=50)

    # Aggregate number of css issues from all scans in all user agents
    css_issues = models.IntegerField(max_length=50)

    # Aggregate number of sniffing issues detected in this site scan
    ua_issues = models.IntegerField(max_length=50)


    def __unicode__(self):
        return u"'Site scanned has ({0}) css issues and ({1}) ua issues".format(self.css_issues, self.ua_issues)


class URLScanData(models.Model):
    """
    Aggregate data model for url scans (all scans of this url with all the
    different user agents)
    """
    urlscan = models.OneToOneField(URLScan)

    # Other metrics
    num_rules = models.IntegerField(max_length=50)
    num_properties = models.IntegerField(max_length=50)
    scanned_pages = models.IntegerField(max_length=50)

    # Aggregate css_issues from all linked css stylesheets
    css_issues = models.IntegerField(max_length=50)

    # If the url scan had a user agent issue (recognized non-primary mobile ua
    # but not the primary mobile ua)
    ua_issues = models.BooleanField(default=False)

    def __unicode__(self):
        return u"'URL scanned has ({0}) css issues and ({1}) ua issues".format(self.css_issues, self.ua_issues)


class URLContentData(models.Model):
    """
    Aggregate data model for url content (a particular scan using a particular
    user agent)
    """
    urlcontent = models.OneToOneField(URLContent)

    # Other metrics
    num_rules = models.IntegerField(max_length=50)
    num_properties = models.IntegerField(max_length=50)

    # Aggregate css_issues from all linked css stylesheets
    css_issues = models.IntegerField(max_length=50)

    def __unicode__(self):
        return u"'Page scanned with user agent '{0}' has ({1}) css issues".format(
            self.urlcontent.user_agent, self.css_issues)


class LinkedCSSData(models.Model):
    """ Aggregate data model for linked css stylesheet """
    linked_css = models.OneToOneField(LinkedCSS)

    # These seem to be useful statistics to collect that we can drill down to
    num_rules = models.IntegerField(max_length=50)
    num_properties = models.IntegerField(max_length=50)

    # Number of places where a rule used a prefixed property but no moz prefix
    css_issues = models.IntegerField(max_length=50)

    def __unicode__(self):
        return u"'Linked CSS stylesheet has ({0}) css issues".format(
            self.css_issues)
