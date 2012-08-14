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
        pass

    def aggregate_batch(batch):
        """
        Given a particular batch,
        """

    def aggregate():
        """
        For each relevant batch, traverse the scan tree and aggregate data
        """

        # Identify the relevant batches:
        if self.selection == "new":
            batches =
        elif self.selection == "all":
            batches =
        elif self.selection == "single":
            batches =
        else:
            batches = []

        for batch in batches:
            aggregate_batch(batch)
