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
    def __init__(self, selection="new", batch=None):
        """
        Initialize aggregator object. Takes a selection type, and a batch only
        if being initialized with a single batch in mind (vs a set of batches)
        """
        self.selection = selection
        self.batch = batch

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
        Given a particular batch, aggregate the stats from its children
        """
        pass

    def aggregate_sitescan(self, sitescan):
        """
        Given a particular sitescan, aggregate the stats from its children
        """
        pass

    def aggregate_urlscan(self, urlscan):
        """
        Given a particular urlscan, aggregate the stats from its children
        """
        pass

    def aggregate_urlcontent(self, urlcontent):
        """
        Given a particular urlcontent, aggregate the stats from its children
        """
        pass

    def aggregate__linkedcss(self, linkedcss):
        """
        Given a particular linkedcss, aggregate the stats from its children
        """
        pass

    def aggregate(self):
        """
        For each relevant batch, traverse the scan tree and aggregate data
        """

        # Identify the relevant batches:
        if self.selection == "new":
            batches = models.Batch.objects.filter(data_aggregated=False)
        elif self.selection == "all":
            batches = models.Batch.objects.all()
        elif self.selection == "single":
            batches = [self.batch]
        else:
            batches = []

        for batch in batches:
            # Set off chain reaction for aggregation
            self.aggregate_batch(batch)




