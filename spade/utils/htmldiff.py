from lxml import etree
from Queue import Queue
from StringIO import StringIO

import difflib


class HTMLDiff(object):
    def __init__(self):
        self.layers = 0

    def compare(self, html1, html2):
        """Compare two html strings"""
        html1 = self.strip(html1)
        html2 = self.strip(html2)

        # Get difflib ratio
        s = difflib.SequenceMatcher(None, html1, html2)
        return s.ratio()

    def strip(self, html):
        """Remove text elements from the html, as well as element attrs"""
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html), parser)

        # Clear attributes and text, to get bare html
        for element in tree.iter():
            element.text = ""
            for key in element.keys():
                del element.attrib[key]

        return etree.tostring(tree)
