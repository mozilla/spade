"""
Spade models.

"""
from datetime import datetime

from django.db import models

from spade.utils.misc import get_domain

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


class Issue(models.Model):
    ISSUE_TYPE_CHOICES = enumerate(['ua sniffing', 'css prefix'])
    name = models.CharField(max_length=255, unique=True)
    issue_type = models.PositiveSmallIntegerField(choices=ISSUE_TYPE_CHOICES)
    description = models.TextField(blank=True)


class Url(models.Model):
    page_url = models.TextField()
    # page_url should be unique.
    # since it's a text field, we put its hash in that constraint
    page_url_hash = models.CharField(max_length=64, unique=True)


class Site(models.Model):
    url = models.ForeignKey(Url, unique=True)
    issues = models.ManyToManyField(Issue, related_name='sites')


class UserAgent(models.Model):
    """Base common class for UserAgent and BatchUserAgent."""
    DESKTOP = 0
    MOBILE = 1
    UA_TYPE_CHOICES = (
        (DESKTOP, 'desktop'),
        (MOBILE, 'mobile'),
    )
    UA_TYPES = dict(UA_TYPE_CHOICES)

    ua_human_name = models.CharField(max_length=50)
    ua_string = models.CharField(max_length=250, unique=True)
    ua_type = models.IntegerField(max_length=1, choices=UA_TYPE_CHOICES,
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

STATUS_LIST = [
    "Not started",
    "Started",
    "Failed",
    "Finished"
]

STATUS_CHOICES = enumerate(STATUS_LIST)
STATUS_DICT = dict((v, k) for k, v in STATUS_CHOICES)


class Batch(models.Model):

    """ A batch of sites scanned in one run. """
    kickoff_time = models.DateTimeField("When crawl started",
                                        auto_now_add=True, unique=True)
    finish_time = models.DateTimeField("When crawl ended",
                                       blank=True, null=True)
    scan_status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES,
                                                   default=1)
    aggregation_status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=1)
    sites = models.ManyToManyField(Site)
    user_agents = models.ManyToManyField(
        UserAgent,
        through='BatchUserAgent'
        related_name='batches')

    @property
    def bad_sites(self):
        """ Returns a list of site urls that did not get scraped """
        return self.sites_scanned.filter(scan_status=STATUS_DICT['Failed'])

    def __unicode__(self):
        return u"Batch started at {0}".format(self.kickoff_time)

    class Meta:
        verbose_name_plural = u"batches"


class BatchUserAgent(models.Model):
    """
    Holds the relation between a batch and a user_agent
    """
    batch = models.ForeignKey(Batch)
    ua_string = models.CharField(max_length=250)
    user_agent = models.ForeignKey(UserAgent)

    class Meta:
        unique_together = [("batch", "user_agent")]


class SiteScan(models.Model):
    """ An individual site scanned. """
    scan_status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES,
                                                   default=1)
    kickoff_time = models.DateTimeField("When crawl started",
                                        auto_now_add=True, unique=True)
    finish_time = models.DateTimeField("When crawl ended",
                                       blank=True, null=True)
    batch = models.ForeignKey(Batch, db_index=True,
                              related_name='sites_scanned')
    site = models.ForeignKey(Site, related_name="scan_set")

    def __unicode__(self):
        return self.site.url

    class Meta:
        unique_together = ("batch", "site")


class URLScan(models.Model):
    """
    An individual URL scanned.

    For each ``SiteScan``, we follow links one level deep from the entry page,
    so every ``SiteScan`` will have a number of associated ``URLScan``s, one
    for the entry page URL and one for each link followed.
    """

    site_scan = models.ForeignKey(SiteScan, db_index=True)
    url = models.ForeignKey(Url)
    timestamp = models.DateTimeField("timestamp")

    def __unicode__(self):
        return self.page_url

    class Meta:
        unique_together = ("site_scan", "url")


class CssFile(models.Model):
    """
    A url pointing to a css resource.
    Different css files can share the same content
    """
    url = models.ForeignKey(Url)
    content = models.ForeignKey(CssContent, related_name='css_files')
    timestamp = models.DateTimeField("timestamp", auto_now_add=True)

    class Meta:
        unique_together = ['url', 'content', 'timestamp']


class CssContent(models.Model):

    raw_css = models.FileField(max_length=500, upload_to=css_filename)
    content_hash = models.CharField(max_length=64, unique=True, blank=True)

    def __unicode__(self):
        return self.content_hash


class CSSRule(models.Model):
    """ A CSS element rule """
    css_content = models.ForeignKey(CssContent)
    selector = models.TextField()
    select_hash = models.CharField(max_length=64, unique=True, blank=True)

    def __unicode__(self):
        return self.selector

    class Meta:
        unique_together = ['css_content', 'selector_hash']


class CSSProperty(models.Model):
    """ A CSS property belonging to a rule """
    rule = models.ForeignKey(CSSRule, related_name='properties')
    prefix = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __unicode__(self):
        ret = u"%s%s: %s" % (self.prefix, self.name, self.value)

        return ret

    @property
    def full_name(self):
        return '%s%s' % (self.prefix, self.name)

    class Meta:
        unique_together = ['rule', 'prefix', 'name']


class CSSPropertyData(models.Model):
    """ Aggregated data for fast outputting """
    css_content = models.ManyToManyField(CssContent,
                                         related_name='aggregated_properties')
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
        return (
            self.moz_count >= self.webkit_count or
            self.unpref_count >= self.webkit_count
        )

    @property
    def prefix_diff(self):
        """ The higher this is, the worse the moz support is """
        return self.webkit_count - self.moz_count


class URLContent(models.Model):
    """
    The content for a particular user-agent from one scanned URL.

    Stores raw markup and headers; linked CSS and JS are stored in the
    ``LinkedCSS`` and ``LinkedJS`` tables.

    """
    url_scan = models.ForeignKey(URLScan)
    user_agent = models.ForeignKey(BatchUserAgent)
    redirected_from = models.ForeignKey(Url, blank=True, null=True)
    raw_markup = models.FileField(
        max_length=500, upload_to=html_filename)
    headers = models.FileField(
        max_length=500, upload_to=headers_filename)
    css = models.MantToMany(CssFile, related_name='referring_page')

    def __unicode__(self):
        return u"'{0}' scanned with '{1}'".format(
            self.url_scan, self.user_agent.ua_string)


class JsFile(models.Model):
    """
    A url pointing to a js resource.
    Different js files can share the same content
    """
    url = models.ForeignKey(Url)
    content = models.ForeignKey(JsContent, related_name='js_files')
    timestamp = models.DateTimeField("timestamp", auto_now_add=True)

    class Meta:
        unique_together = ['url', 'content', 'timestamp']


class JsContent(models.Model):

    raw_js = models.FileField(max_length=500, upload_to=js_filename)
    content_hash = models.CharField(max_length=64, unique=True, blank=True)

    def __unicode__(self):
        return self.content_hash


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
    sitescan = models.OneToOneField(SiteScan, null=True)

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
