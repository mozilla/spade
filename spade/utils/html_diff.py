import difflib

from lxml.html.clean import Cleaner


class HTMLDiff(object):
    def __init__(self):
        self.layers = 0

    def compare(self, html1, html2):
        """Compare two html strings"""
        html1 = self.strip(html1)
        html2 = self.strip(html2)

        s = difflib.SequenceMatcher(None, html1, html2)
        return s.ratio()

    def strip(self, html):
        """Remove text elements from the html, as well as element attrs"""
        cleaner = Cleaner(scripts=True, javascript=True, comments=True,
            style=True, embedded=True)

        h = html.read()
        # strip non ascii chars
        h = ''.join(c for c in h if ord(c) < 128)
        html.seek(0)  # hack to have the file re-readable for further checking

        return cleaner.clean_html(h)
