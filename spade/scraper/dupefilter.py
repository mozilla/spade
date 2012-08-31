"""
A custom duplicate-request filter.

"""
import os

from scrapy.dupefilter import RFPDupeFilter
from scrapy.utils.request import request_fingerprint



class MultipleUADupeFilter(RFPDupeFilter):
    """A dupe filter that considers the User-Agent header."""

    def request_seen(self, request):
        fp = request_fingerprint(request, ["User-Agent"])
        if fp in self.fingerprints:
            return True
        self.fingerprints.add(fp)
        if self.file:
            self.file.write(fp + os.linesep)
