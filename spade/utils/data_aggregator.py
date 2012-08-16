"""
Class to perform data aggregation for completed scans

"""
from spade import model


class DataAggregator(object):

    def __init__(selection="new", batch=None):
        """
        Initialize aggregator object. Takes a selection type, and a batch only
        if being initialized with a single batch in mind (vs a set of batches)
        """
        self.selection = selection
        self.batch = batch

    def detect_ua_issue(urlscan):
        """
        Given a urlscan, look at the different user agents used and determine
        whether there is a UA sniffing issue
        """
        urlcontents = model.URLContent.objects.filter(url_scan=urlscan)
        
        # Prepare some storage for the urlcontents' user agent
        desktop_uas = []
        mobile_uas = []
        primary_ua = None

        for urlcontent in urlcontents:
            if urlcontent.user_agent.ua_type == 'desktop'
            if urlcontent.user_agent.primary_ua
            

        pass

    def aggregate_batch(batch):
        """
        Given a particular batch, aggregate the statistics from its children
        """

    def aggregate_sitescan(sitescan):
        """
        """
        pass

    def aggregate_urlscan(urlscan):
        """
        """
        pass

    def aggregate_urlcontent(urlcontent):
        """
        """
        pass

    def aggregate__linkedcss(linkedcss):
        """
        """
        pass

    def aggregate():
        """
        For each relevant batch, traverse the scan tree and aggregate data
        """

        # Identify the relevant batches:
        if self.selection == "new":
            batches = model.Batch.objects.filter(data_aggregated=False)
        elif self.selection == "all":
            batches = model.Batch.objects.all()
        elif self.selection == "single":
            batches = [self.batch]
        else:
            batches = []

        for batch in batches:
            # Set off chain reaction for aggregation
            self.aggregate_batch(batch)




