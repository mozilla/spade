"""
Spade models.

"""
from datetime import datetime

from django.db import models


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


class BaseUserAgent(models.Model):
    """Base common class for UserAgent and BatchUserAgent."""
    DESKTOP = 0
    MOBILE = 1
    UA_TYPE_CHOICES = (
        (DESKTOP, 'desktop'),
        (MOBILE, 'mobile'),
    )
    UA_TYPES = dict(UA_TYPE_CHOICES)

    ua_human_name = models.CharField(max_length=50)
    ua_string = models.CharField(max_length=250)
    ua_type = models.IntegerField(max_length=1,
                                  choices=UA_TYPE_CHOICES,
                                  default=DESKTOP)
    primary_ua = models.BooleanField(default=False)

    def __unicode__(self):
        if self.ua_human_name:
            return unicode(self.ua_human_name)
        return unicode(self.ua_string)

    def __repr__(self):
        tags = self.UA_TYPES[self.ua_type]
        if self.primary_ua:
            tags += ", primary"
        return u"<(%s) %s: '%s'>" % (tags, self.ua_human_name, self.ua_string)

    class Meta:
        abstract = True


class UserAgent(BaseUserAgent):
    """ A user-agent string we will use for scanning. """
    pass


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


class BatchUserAgent(BaseUserAgent):
    """
    A user agent from a given batch.

    Clones the UserAgent model, so that we can retain history for scan UAs
    while allowing the user to add/remove/modify user agents for future
    batches.

    """
    batch = models.ForeignKey(Batch)

    class Meta:
        unique_together = [("batch", "ua_string")]


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
    """A single linked CSS file."""
    batch = models.ForeignKey(Batch)
    linked_from = models.ManyToManyField(URLContent)
    url = models.TextField()
    url_hash = models.CharField(max_length=64)
    raw_css = models.FileField(
        max_length=500, upload_to=css_filename)

    def __unicode__(self):
        return self.url

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
        return self.url

    class Meta:
        verbose_name_plural = "Linked JS"


class CSSRule(models.Model):
    """ A CSS element rule """
    linkedcss = models.ForeignKey(LinkedCSS)
    selector = models.TextField()

    def __unicode__(self):
        return self.selector


class CSSProperty(models.Model):
    """ A CSS property belonging to a rule """
    rule = models.ForeignKey(CSSRule)
    prefix = models.CharField(max_length=50)
    name = models.TextField()
    value = models.TextField()

    def __unicode__(self):
        ret = u"%s%s: %s" % (self.prefix, self.name, self.value)

        return ret

    @property
    def full_name(self):
        return '%s%s' % (self.prefix, self.name)


class CSSPropertyData(models.Model):
    """ Aggregated data for fast outputting """
    linkedcsss = models.ManyToManyField(LinkedCSS, related_name='cssproperties')
    sitescan = models.ForeignKey(SiteScan)
    name = models.CharField(max_length=100)
    moz_count = models.IntegerField(default=0)
    webkit_count = models.IntegerField(default=0)
    unpref_count = models.IntegerField(default=0)

    def __unicode__(self):
        return '%s: moz %d, webkit %d, unpref %d' %\
            (self.name, self.moz_count, self.webkit_count, self.unpref_count)

    @property
    def supports_moz(self):
        return self.moz_count >= self.webkit_count

    @property
    def prefix_diff(self):
        """ The higher this is, the worse the moz support is """
        return self.webkit_count - self.moz_count

""" Aggregate Data Models """


class BatchData(models.Model):
    """ Aggregate data model for scan batches """
    batch = models.OneToOneField(Batch)

    # Other metrics
    num_rules = models.IntegerField()
    num_properties = models.IntegerField()
    scanned_pages = models.IntegerField()

    # Aggregate number of css issues from all scans in all user agents
    css_issues = models.IntegerField()

    # Aggregate number of UA issues in this batch
    ua_issues = models.IntegerField()

    css_issues_regressed = models.IntegerField(null=True)
    css_issues_fixed = models.IntegerField(null=True)
    ua_issues_regressed = models.IntegerField(null=True)
    ua_issues_fixed = models.IntegerField(null=True)

    def __unicode__(self):
        return u"'{0}' has ({1}) css issues and ({2}) ua issues".format(
            self.batch, self.css_issues, self.ua_issues)

    @property
    def css_issues_pctg(self):
        total = 0
        issues = 0
        for sitescan in self.batch.sitescan_set.iterator():
            data = sitescan.sitescandata
            total += 1
            if data.css_issues:
                issues += 1
        if total == 0:
            return 0.0
        return issues * 100.0 / total

    @property
    def ua_issues_pctg(self):
        total = 0
        issues = 0
        for sitescan in self.batch.sitescan_set.iterator():
            data = sitescan.sitescandata
            total += 1
            if data.ua_issues:
                issues += 1
        if total == 0:
            return 0.0
        return issues * 100.0 / total


class SiteScanData(models.Model):
    """ Aggregate data model for site scans """
    sitescan = models.OneToOneField(SiteScan)

    # Other metrics
    num_rules = models.IntegerField()
    num_properties = models.IntegerField()
    scanned_pages = models.IntegerField()

    # Aggregate number of css issues from all scans in all user agents
    css_issues = models.IntegerField()

    # Does the website have issues sniffing our UA?
    ua_issues = models.BooleanField(default=False)


    def __unicode__(self):
        return u"'{0}' has ({1}) css issues and ({2}) ua issues".format(
            self.sitescan, self.css_issues, self.ua_issues)


class URLScanData(models.Model):
    """
    Aggregate data model for url scans (all scans of this url with all the
    different user agents)
    """
    urlscan = models.OneToOneField(URLScan)

    # Other metrics
    num_rules = models.IntegerField()
    num_properties = models.IntegerField()

    # Aggregate css_issues from all linked css stylesheets
    css_issues = models.IntegerField()


    def __unicode__(self):
        return u"'{0}' has ({1}) css issues".format(
            self.urlscan, self.css_issues)


class URLContentData(models.Model):
    """
    Aggregate data model for url content (a particular scan using a particular
    user agent)
    """
    urlcontent = models.OneToOneField(URLContent)

    # Other metrics
    num_rules = models.IntegerField()
    num_properties = models.IntegerField()

    # Aggregate css_issues from all linked css stylesheets
    css_issues = models.IntegerField(max_length=50)

    def __unicode__(self):
        return u"{0} has ({1}) css issues".format(
            self.urlcontent, self.css_issues)


class MarkupDiff(models.Model):
    """ How much two versions of the same website
    served for different UAs are alike """

    sitescan = models.ForeignKey(SiteScan)
    first_ua = models.ForeignKey(BatchUserAgent, related_name='ua1')
    second_ua = models.ForeignKey(BatchUserAgent, related_name='ua2')
    percentage = models.FloatField(default=0.0)

    def __unicode__(self):
        s1 = unicode(self.first_ua)
        s2 = unicode(self.second_ua)
        return u'%s vs %s: %.2f%%' % (s1, s2, self.percentage)


class LinkedCSSData(models.Model):
    """ Aggregate data model for linked css stylesheet """
    linked_css = models.OneToOneField(LinkedCSS)

    # These seem to be useful statistics to collect that we can drill down to
    num_rules = models.IntegerField()
    num_properties = models.IntegerField()

    # Number of places where a rule used a prefixed property but no moz prefix
    css_issues = models.IntegerField()

    def __unicode__(self):
        return u"'{0}' has ({1}) css issues".format(
            self.linked_css, self.css_issues)
