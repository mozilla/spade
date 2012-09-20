"""
Class to perform data aggregation for completed scans

"""
from django.db import transaction

from spade import model
from spade.utils.html_diff import HTMLDiff
from spade.utils.misc import get_domain
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
    def get_sitescan(site_url_hash, batch):
        sitescan = batch.sitescan_set.filter(site_url_hash=site_url_hash)
        if sitescan.count():
            return sitescan[0]
        return None

    @staticmethod
    def get_csspropdata(name, sitescan):
        props = sitescan.csspropertydata_set.filter(name=name)
        if props.count():
            return props[0]
        return None


class RegressionHunter(object):
    @staticmethod
    def get_ua_diffs(previous_batch, current_batch):
        """ Returns a 2-tuple containing a list of regressions
        and a list of fixes """

        regressions = []
        fixes = []
        for site in current_batch.sitescan_set.iterator():
            prev = DBUtils.get_sitescan(site.site_url_hash, previous_batch)
            if not prev:
                continue
            if not prev.sitescandata.ua_issues and site.sitescandata.ua_issues:
                regressions.append(site)
            elif prev.sitescandata.ua_issues and not site.sitescandata.ua_issues:
                fixes.append(site)

        return (regressions, fixes)

    @staticmethod
    def get_css_diffs(previous_batch, current_batch):
        """ Returns a 2-tuple containing a list of regressions
        and a list of fixes """

        regressions = []
        fixes = []

        # check for every sitescan
        for sitescan in current_batch.sitescan_set.iterator():
            # find the equivalent sitescan in the previous batch (if any)
            prev = DBUtils.get_sitescan(sitescan.site_url_hash, previous_batch)
            if not prev:
                continue
            for prop_data in sitescan.csspropertydata_set.iterator():
                # find the equivalent prop_data in the prev sitescan
                prev_prop_data = DBUtils.get_csspropdata(prop_data.name, prev)
                if not prev_prop_data:
                    continue

                # check to see if issue has been totally fixed / regressed
                if prev_prop_data.supports_moz and not prop_data.supports_moz:
                    regressions.append(prop_data)
                    continue
                elif not prev_prop_data.supports_moz and prop_data.supports_moz:
                    fixes.append(prop_data)
                    continue

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
        # find all the invalid sitescans and delete them
        requested_domains = [get_domain(s) for s in batch.sites]
        for sitescan in batch.sitescan_set.iterator():
            if not get_domain(sitescan.site_url) in requested_domains:
                sitescan.delete()

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
            total_ua_issues += 1 if sitescan_data.ua_issues else 0

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

        # Aggregate data for each urlscan
        for urlscan in urlscans:
            urlscan_data = self.aggregate_urlscan(urlscan)
            total_rules += urlscan_data.num_rules
            total_properties += urlscan_data.num_properties
            total_pages_scanned += 1

        # figure out the number of distinct css property issues
        css_issues = 0
        for prop_data in sitescan.csspropertydata_set.iterator():
            if prop_data.moz_count < prop_data.webkit_count:
                css_issues += 1

        # figure out if the website does UA sniffing or not
        ua_issues = self.detect_ua_issue(sitescan)

        # Create this sitescan's data model
        return model.SiteScanData.objects.create(
            sitescan=sitescan,
            num_rules=total_rules,
            num_properties=total_properties,
            scanned_pages=total_pages_scanned,
            css_issues=css_issues,
            ua_issues=ua_issues,
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

        sitescan = linkedcss.linked_from.all()[0].url_scan.site_scan
        for webkit_prop in webkit_props:
            name = webkit_prop[8:]  # strip away the prefix
            # check to see if we already have a cssprop data object for this
            data = model.CSSPropertyData.objects.filter(name=name, sitescan=sitescan)
            if len(data):
                data = data[0]
            else:
                data = model.CSSPropertyData.objects.create(name=name, sitescan=sitescan)
            data.linkedcsss.add(linkedcss)
            webkit_count = self.get_prop_count(linkedcss, webkit_prop)
            if webkit_prop not in self.props:
                # just add it to self.props and go on as if it were there
                self.props[webkit_prop] = ('-moz-%s' % name, name)
            moz_equiv = self.props[webkit_prop][0]
            unpref_equiv = self.props[webkit_prop][1]
            moz_count = self.get_prop_count(linkedcss, moz_equiv)
            unpref_count = self.get_prop_count(linkedcss, unpref_equiv)

            if webkit_count > moz_count and webkit_count > unpref_count:
                total_css_issues += 1

            data.webkit_count += webkit_count
            data.moz_count += moz_count
            data.unpref_count += unpref_count
            data.save()

        # Create this linkedcss's data model
        return model.LinkedCSSData.objects.create(
            linked_css=linkedcss,
            num_rules=total_rules,
            num_properties=total_properties,
            css_issues=total_css_issues,
            )

    def detect_ua_issue(self, sitescan):
        """
        Given a sitescan, look at the different user agents used and determine
        whether there is a UA sniffing issue
        ! Only checks the main (as in top level) page. !
        """
        diff_util = HTMLDiff()

        # find the main page urlscan (if any)
        urlscans = sitescan.urlscan_set.filter(page_url=sitescan.site_url)
        if urlscans.count():
            urlcontents = list(urlscans[0].urlcontent_set.all())
        else:
            urlcontents = []

        nr = len(urlcontents)

        # if we have less urlcontents than UAs, check for redirects,
        # like m.yahoo.com from yahoo.com
        if nr < sitescan.batch.batchuseragent_set.count():
            # look in all urlscans
            for urlscan in sitescan.urlscan_set.iterator():
                # for urlcontents of pages redirected from the homepage
                redirs = urlscan.urlcontent_set.filter(redirected_from=
                                                       sitescan.site_url)
                if not redirs.count():
                    continue
                for mobile_homepage_content in redirs:
                        urlcontents.append(mobile_homepage_content)
        # update the number of urlcontents we need to check
        nr = len(urlcontents)

        for i in xrange(nr):
            for j in xrange(i + 1, nr):
                content1 = urlcontents[i]
                content2 = urlcontents[j]
                if content1 == content2:
                    continue
                similarity = diff_util.compare(content1.raw_markup,
                                               content2.raw_markup)
                percentage = similarity * 100
                model.MarkupDiff.objects.create(sitescan=sitescan,
                                                first_ua=content1.user_agent,
                                                second_ua=content2.user_agent,
                                                percentage=percentage)
        return False # FIXME!
        # this needs to return True or False depending on the fact that we
        # consider the site as having a UA sniffing issue or not
        # this must be replaced after we agree on when a site has an UA issue
