"""
Class to perform data aggregation for completed scans

"""
from django.db import transaction

from spade import model
from spade.utils.html_diff import HTMLDiff
from spade.utils.read_props import read_props
from spade.settings.base import CSS_PROPS_FILE

# This constant determines the lowest similarity bound for two pages to still
# be considered the same content.
SIMILARITY_CONSTANT = 0.9


class AggregationError(Exception):
    pass


class DBUtils(object):
    @staticmethod
    def get_previous_batch(batch):
        prev_batches = model.Batch.objects.filter(finish_time__lt=batch.finish_time)
        prev = prev_batches.order_by('-finish_time')[:1]
        if prev:
            return prev[0]
        return None

    @staticmethod
    def get_url_scan(url, batch):
        urls = model.URLScan.objects.filter(site_scan__batch__id=batch.id)
        urls = urls.filter(page_url=url.page_url)
        if urls.count():
            return urls[0]
        return None

    @staticmethod
    def get_linkedcss(url, batch):
        css = batch.linkedcss_set.filter(url=url)
        if css.count():
            return css[0]
        return None

    @staticmethod
    def get_csspropdata(name, linkedcss):
        props = linkedcss.csspropertydata_set.filter(name=name)
        if props.count():
            return props[0]
        return None


class RegressionHunter(object):
    @staticmethod
    def get_ua_diffs(previous_batch, current_batch):
        """ Returns a 2-tuple containing a list of regressions
        and a list of fixes """

        # get a list of the urls scanned in the current batch
        urls = []
        for site_scan in current_batch.sitescan_set.iterator():
            for url in site_scan.urlscan_set.iterator():
                urls.append(url)

        # TODO: maybe use directly the iterators above and do not save the urls

        regressions = []
        fixes = []
        for url in urls:
            prev = DBUtils.get_url_scan(url, previous_batch)
            if not prev:
                continue
            if not prev.urlscandata.ua_issue and url.urlscandata.ua_issue:
                regressions.append(url)
            elif prev.urlscandata.ua_issue and not url.urlscandata.ua_issue:
                fixes.append(url)

        return (regressions, fixes)

    @staticmethod
    def get_css_diffs(previous_batch, current_batch):
        """ Returns a 2-tuple containing a list of regressions
        and a list of fixes """

        regressions = []
        fixes = []

        # current linkedCSSs
        for linkedcss in current_batch.linkedcss_set.iterator():
            # find the equivalent linkedcss in the previous batch (if any)
            prev = DBUtils.get_linkedcss(linkedcss.url, previous_batch)
            if not prev:
                continue
            for prop_data in linkedcss.csspropertydata_set.iterator():
                # find the equivalent prop_data in the prev linkedcss
                prev_prop_data = DBUtils.get_csspropdata(prop_data.name, prev)
                if not prev_prop_data:
                    continue
                if prev_prop_data.supports_moz and not prop_data.supports_moz:
                    regressions.append(prop_data)
                elif not prev_prop_data.supports_moz and prop_data.supports_moz:
                    fixes.append(prop_data)

        return (regressions, fixes)


class DataAggregator(object):
    def __init__(self):
        self.props = read_props(CSS_PROPS_FILE)

    @transaction.commit_on_success
    def aggregate_batch(self, batch):
        """
        Given a particular batch, aggregate the stats from its children into
        the data model and return it
        """
        sitescans = model.SiteScan.objects.filter(batch=batch).iterator()

        # Initialize counters
        total_rules = 0
        total_properties = 0
        total_pages_scanned = 0
        total_css_issues = 0
        total_ua_issues = 0

        # Aggregate data for each sitescan
        for sitescan in sitescans:
            sitescan_data = self.aggregate_sitescan(sitescan)
            total_rules += sitescan_data.num_rules
            total_properties += sitescan_data.num_properties
            total_pages_scanned += sitescan_data.scanned_pages
            total_css_issues += sitescan_data.css_issues
            total_ua_issues += sitescan_data.ua_issues

        # Actually update the batchdata field
        data = model.BatchData.objects.create(
            batch=batch,
            num_rules=total_rules,
            num_properties=total_properties,
            scanned_pages=total_pages_scanned,
            css_issues=total_css_issues,
            ua_issues=total_ua_issues,
            )

        # Count and store regressions and fixes
        prev = DBUtils.get_previous_batch(batch)
        if prev and prev.data_aggregated:
            regressions, fixes = RegressionHunter.get_ua_diffs(prev, batch)
            data.ua_issues_regressed = len(regressions)
            data.ua_issues_fixed = len(fixes)
            regressions, fixes = RegressionHunter.get_css_diffs(prev, batch)
            data.css_issues_regressed = len(regressions)
            data.css_issues_fixed = len(fixes)
            data.save()

        # Mark the batch complete
        batch.data_aggregated = True
        batch.save()

    @transaction.commit_on_success
    def aggregate_sitescan(self, sitescan):
        """
        Given a particular sitescan, aggregate the stats from its children into
        the data model and return it
        """
        urlscans = model.URLScan.objects.filter(site_scan=sitescan).iterator()

        # Initialize counters
        total_rules = 0
        total_properties = 0
        total_pages_scanned = 0
        total_css_issues = 0
        total_ua_issues = 0

        # Aggregate data for each urlscan
        for urlscan in urlscans:
            urlscan_data = self.aggregate_urlscan(urlscan)
            total_rules += urlscan_data.num_rules
            total_properties += urlscan_data.num_properties
            total_pages_scanned += 1
            total_css_issues += urlscan_data.css_issues
            if urlscan_data.ua_issue:
                total_ua_issues += 1

        # Create this sitescan's data model
        return model.SiteScanData.objects.create(
            sitescan=sitescan,
            num_rules=total_rules,
            num_properties=total_properties,
            scanned_pages=total_pages_scanned,
            css_issues=total_css_issues,
            ua_issues=total_ua_issues,
            )

    @transaction.commit_on_success
    def aggregate_urlscan(self, urlscan):
        """
        Given a particular urlscan, aggregate the stats from its children into
        the data model and return it
        """
        urlcontents = model.URLContent.objects.filter(url_scan=urlscan).iterator()

        # Initialize counters
        total_rules = 0
        total_properties = 0
        total_css_issues = 0
        ua_issue = False

        # Detect user agent sniffing issues
        try:
            if self.detect_ua_issue(urlscan):
                ua_issue = True
        except AggregationError as e:
            print "Unable to detect UA-sniffing issues for '%s': %s" % (
                urlscan, e)

        # Aggregate data for each urlcontent
        for urlcontent in urlcontents:
            urlcontent_data = self.aggregate_urlcontent(urlcontent)
            total_rules += urlcontent_data.num_rules
            total_properties += urlcontent_data.num_properties
            total_css_issues += urlcontent_data.css_issues

        # Create this urlscan's data model
        return model.URLScanData.objects.create(
            urlscan=urlscan,
            num_rules=total_rules,
            num_properties=total_properties,
            css_issues=total_css_issues,
            ua_issue=ua_issue,
            )

    @transaction.commit_on_success
    def aggregate_urlcontent(self, urlcontent):
        """
        Given a particular urlcontent, aggregate the stats from its children
        into the data model and return it
        """
        linkedstyles = model.LinkedCSS.objects.filter(linked_from=urlcontent)

        # Initialize counters
        total_rules = 0
        total_properties = 0
        total_css_issues = 0

        # Aggregate data for each linked css stylesheet
        for linkedcss in linkedstyles:
            linkedcss_data = self.aggregate_linkedcss(linkedcss)
            total_rules += linkedcss_data.num_rules
            total_properties += linkedcss_data.num_properties
            total_css_issues += linkedcss_data.css_issues

        # Create this urlcontent's data model
        return model.URLContentData.objects.create(
            urlcontent=urlcontent,
            num_rules=total_rules,
            num_properties=total_properties,
            css_issues=total_css_issues,
            )

    def get_prop_count(self, css, prop_name):
        if not prop_name:
            return 0
        count = 0
        for rule in css.cssrule_set.iterator():
            for prop in rule.cssproperty_set.iterator():
                if prop.full_name == prop_name:
                    count += 1
        return count

    @transaction.commit_on_success
    def aggregate_linkedcss(self, linkedcss):
        """
        Given a particular linkedcss, aggregate the stats from its children
        into the data model and return it
        """
        # A single LinkedCSS can be linked from multiple URLContents, thus we
        # have to check if its already been evaluated. (TODO we could keep an
        # in-memory cache of these to save db queries, if needed to help
        # performance)
        try:
            return model.LinkedCSSData.objects.get(linked_css=linkedcss)
        except model.LinkedCSSData.DoesNotExist:
            pass

        print "Aggregating CSS data for %s" % linkedcss.url

        # Initialize counters
        total_rules = model.CSSRule.objects.filter(linkedcss=linkedcss).count()
        total_properties = model.CSSProperty.objects.filter(
            rule__linkedcss=linkedcss).count()
        total_css_issues = 0

        # find all webkit properties
        webkit_props = set()
        for rule in linkedcss.cssrule_set.iterator():
            for webkit_prop in rule.cssproperty_set.filter(prefix='-webkit-').iterator():
                webkit_props.add(webkit_prop.full_name)

        for webkit_prop in webkit_props:
            name = webkit_prop[8:]  # strip away the prefix
            data = model.CSSPropertyData(linkedcss=linkedcss, name=name)
            data.webkit_count = self.get_prop_count(linkedcss, webkit_prop)
            if webkit_prop not in self.props:
                total_css_issues += 1
                data.moz_count = 0
                data.unpref_count = 0
                data.save()
                continue
            moz_equiv = self.props[webkit_prop][0]
            unpref_equiv = self.props[webkit_prop][1]
            data.moz_count = self.get_prop_count(linkedcss, moz_equiv)
            data.unpref_count = self.get_prop_count(linkedcss, unpref_equiv)
            data.save()

            if data.webkit_count > data.moz_count:
                total_css_issues += 1

        # Create this linkedcss's data model
        return model.LinkedCSSData.objects.create(
            linked_css=linkedcss,
            num_rules=total_rules,
            num_properties=total_properties,
            css_issues=total_css_issues,
            )

    def detect_ua_issue(self, urlscan):
        """
        Given a urlscan, look at the different user agents used and determine
        whether there is a UA sniffing issue
        """
        diff_util = HTMLDiff()
        urlcontents = model.URLContent.objects.filter(url_scan=urlscan).iterator()

        # Sort scanned pages by mobile / desktop user agents and find the
        # "primary ua" (the one of interest, the one we want to see was sniffed
        urls_with_desktop_ua = []
        urls_with_mobile_ua = []
        primary_page = None

        for urlcontent in urlcontents:
            if urlcontent.user_agent.primary_ua:
                primary_page = urlcontent
            elif urlcontent.user_agent.ua_type == model.BatchUserAgent.DESKTOP:
                urls_with_desktop_ua.append(urlcontent)
            elif urlcontent.user_agent.ua_type == model.BatchUserAgent.MOBILE:
                urls_with_mobile_ua.append(urlcontent)

        # Ensure we successfully scanned / saved the page with the right user
        # agents before continuing
        if primary_page is None:
            raise AggregationError("No primary mobile user agent!")
        elif len(urls_with_mobile_ua) < 1:
            raise AggregationError("No non-primary mobile user agents!")
        elif len(urls_with_desktop_ua) < 1:
            raise AggregationError("No desktop user agent!")

        # Determine if mobile sniffing happens for other mobile UAs
        mobile_sniff = True
        for mobile_page in urls_with_mobile_ua:
            for desktop_page in urls_with_desktop_ua:
                similarity = diff_util.compare(mobile_page.raw_markup,
                    desktop_page.raw_markup)
                if similarity > SIMILARITY_CONSTANT:
                    mobile_sniff = False

        primary_sniff = False
        if mobile_sniff:
            # If other mobile UAs are sniffed, we want to ensure that we are
            # being sniffed too.
            for desktop_page in urls_with_desktop_ua:
                similarity = diff_util.compare(primary_page.raw_markup,
                    desktop_page.raw_markup)
                if similarity < SIMILARITY_CONSTANT:
                    primary_sniff = True
        else:
            # No issue if other mobiles aren't sniffed
            return False

        return not primary_sniff
