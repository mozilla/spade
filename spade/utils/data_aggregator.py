"""
Class to perform data aggregation for completed scans

"""
from spade.model import models
from spade.utils.html_diff import HTMLDiff

# This constant determines the lowest similarity bound for two pages to still
# be considered the same content.
SIMILARITY_CONSTANT = 0.9


class AggregationError(Exception):
    pass


class DataAggregator(object):
    def __init__(self, selection="new", batch=None, user_agent=None):
        """
        Initialize aggregator object. Takes a selection type, and a batch only
        if being initialized with a single batch in mind (vs a set of batches).

        Also takes an optional user agent, which prevents it from aggregating
        data from other user agents. E.g there are 3 urlcontents from
        mysite.com/index.html being scanned with 3 batchuseragents
        (ie/mozilla/webkit) If we give mozilla's user agent here, only the
        urlcontent that has user_agent="some mozilla / useragent" will be used.
        """
        self.selection = selection
        self.batch = batch

        # Optional, used by the aggregate_urlscan step
        self.user_agent = user_agent

    def detect_ua_issue(self, urlscan):
        """
        Given a urlscan, look at the different user agents used and determine
        whether there is a UA sniffing issue
        """
        diff_util = HTMLDiff()
        urlcontents = models.URLContent.objects.filter(url_scan=urlscan)

        # Sort scanned pages by mobile / desktop user agents and find the
        # "primary ua" (the one of interest, the one we want to see was sniffed
        urls_with_desktop_ua = []
        urls_with_mobile_ua = []
        primary_page = None

        for urlcontent in urlcontents:
            if urlcontent.user_agent.primary_ua:
                primary_page = urlcontent
            elif urlcontent.user_agent.ua_type == models.BatchUserAgent.DESKTOP:
                urls_with_desktop_ua.append(urlcontent)
            elif urlcontent.user_agent.ua_type == models.BatchUserAgent.MOBILE:
                urls_with_mobile_ua.append(urlcontent)

        # Ensure we successfully scanned / saved the page with the right user
        # agents before continuing
        if primary_page is None:
            raise AggregationError("No primary user agent found!")
        elif len(urls_with_mobile_ua) < 1:
            raise AggregationError("Need to define other mobile user agents!")
        elif len(urls_with_desktop_ua) < 1:
            raise AggregationError("No desktop user agents found!")

        # Determine if mobile sniffing happens for other mobile UAs
        mobile_sniff = False
        for mobile_page in urls_with_mobile_ua:
            for desktop_page in urls_with_desktop_ua:
                similarity = diff_util.compare(mobile_page.raw_markup,
                    desktop_page.raw_markup)
                if similarity < SIMILARITY_CONSTANT:
                    mobile_sniff = True

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

    def aggregate_batch(self, batch):
        """
        Given a particular batch, aggregate the stats from its children into
        the data model and return it
        """
        sitescans = models.SiteScan.objects.filter(batch=batch)

        # Initialize counters
        total_rules = 0
        total_properties = 0
        total_pages_scanned = 0
        total_css_issues = 0
        total_ua_issues = 0

        # Aggregate data for each sitescan
        for sitescan in sitescans:
            sitescan_data = aggregate_sitescan(sitescan)
            total_rules += sitescan_data.num_rules
            total_properties += sitescan_data.num_properties
            total_pages_scanned += sitescan_data.scanned_pages
            total_css_issues += sitescan_data.css_issues
            total_ua_issues += sitescan_data.ua_issues

        # Actually update the batchdata field
        batchdata = models.BatchData.objects.create(batch=batch)
        batchdata.num_rules = total_rules
        batchdata.num_properties = total_properties
        batchdata.scanned_pages = total_pages_scanned
        batchdata.css_issues = total_css_issues
        batchdata.ua_issues = total_ua_issues
        batchdata.save()

        # Mark the batch complete
        batch.data_aggregated = True
        batch.save()

    def aggregate_sitescan(self, sitescan):
        """
        Given a particular sitescan, aggregate the stats from its children into
        the data model and return it
        """
        urlscans = models.URLScan.objects.filter(sitescan=sitescan)

        # Initialize counters
        total_rules = 0
        total_properties = 0
        total_pages_scanned = 0
        total_css_issues = 0
        total_ua_issues = 0

        # Aggregate data for each urlscan
        for urlscan in urlscans:
            urlscan_data = aggregate_urlscan(urlscan)
            total_rules += urlscan_data.num_rules
            total_properties += urlscan_data.num_properties
            total_pages_scanned += urlscan_data.scanned_pages
            total_css_issues += urlscan_data.css_issues
            total_ua_issues += urlscan_data.ua_issues

        # Actually update the sitescan field
        sitescandata = models.SiteScanData.objects.create(sitescan=sitescan)
        sitescandata.num_rules = total_rules
        sitescandata.num_properties = total_properties
        sitescandata.scanned_pages = total_pages_scanned
        sitescandata.css_issues = total_css_issues
        sitescandata.ua_issues = total_ua_issues
        sitescandata.save()
        return sitescandata

    def aggregate_urlscan(self, urlscan):
        """
        Given a particular urlscan, aggregate the stats from its children into
        the data model and return it
        """
        urlcontents = models.URLContent.objects.filter(url_scan=urlscan)

        # Initialize counters
        total_rules = 0
        total_properties = 0
        total_pages_scanned = 0
        total_css_issues = 0
        total_ua_issues = 0

        # TODO: determine # pages scanned by counting urlcontents belonging to
        #       this urlscan belonging to a single ua? or all? how??

        #total_pages_scanned =


        # Detect user agent sniffing issues via the class function
        if self.detect_ua_issue(urlscan):
            total_ua_issues += 1

        # Aggregate data for each urlcontent
        # TODO: add a filter that uses user_agent so that we can aggregate
        #       data to only particular user agents rather than all user agents
        for urlcontent in urlcontents:
            urlcontent_data = aggregate_urlcontent(urlcontent)
            total_rules += urlcontent_data.num_rules
            total_properties += urlcontent_data.num_properties
            total_css_issues += urlcontent_data.css_issues

        # Update this urlscan's data model
        urlscandata = models.URLScanData.objects.create(urlscan=urlscan)
        urlscandata.num_rules = total_rules
        urlscandata.num_properties = total_properties
        urlscandata.scanned_pages = total_pages_scanned
        urlscandata.css_issues = total_css_issues
        urlscandata.ua_issues = total_ua_issues
        urlscandata.save()
        return urlscandata

    def aggregate_urlcontent(self, urlcontent):
        """
        Given a particular urlcontent, aggregate the stats from its children
        into the data model and return it
        """
        linkedstyles = models.LinkedCSS.objects.filter(linked_from=urlcontent)

        # Initialize counters
        total_rules = 0
        total_properties = 0
        total_css_issues = 0

        # Aggregate data for each linked css stylesheet
        for linkedcss in linkedstyles:
            linkedcss_data = aggregate_linkedcss(linkedcss)
            total_rules += linkedcss_data.num_rules
            total_properties += linkedcss_data.num_properties
            total_css_issues += linkedcss_data.css_issues

        # Update this urlcontent's data model
        urlcontentdata = models.URLContentData.objects.create(
            urlcontent=urlcontent)
        urlcontentdata.num_rules = total_rules
        urlcontentdata.num_properties = total_properties
        urlcontentdata.css_issues = total_css_issues
        urlcontentdata.save()
        return urlcontentdata

    def aggregate_linkedcss(self, linkedcss):
        """
        Given a particular linkedcss, aggregate the stats from its children
        into the data model and return it
        """
        # Initialize counters
        total_rules = 0
        total_properties = 0
        total_css_issues = 0

        # TODO: Detect how many rules, properties, and css issues exist.

        # Update this linkedcss's data model
        linkedcssdata = models.LinkedCSSData.objects.create(urlscan=urlscan)
        linkedcssdata.num_rules = total_rules
        linkedcssdata.num_properties = total_properties
        linkedcssdata.css_issues = total_css_issues
        linkedcssdata.save()
        return linkedcssdata

    def aggregate(self):
        """
        For each relevant batch, traverse the scan tree and aggregate data
        """

        # Identify the relevant batches:
        if self.selection == "new":
            batches = models.Batch.objects.create(data_aggregated=False)
        elif self.selection == "single":
            batches = [self.batch]
        else:
            batches = models.Batch.objects.all()

        for batch in batches:
            # Set off chain reaction for aggregation
            self.aggregate_batch(batch)
