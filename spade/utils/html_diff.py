import difflib

from lxml.html.clean import Cleaner


class HTMLDiff(object):
    """Utility class that helps to test similarity of html fragments"""

    def compare(self, html1, html2):
        """Compare two html strings"""
        html1 = self.strip(html1)
        html2 = self.strip(html2)

        s = difflib.SequenceMatcher(None, html1, html2)
        return s.ratio()

    def strip(self, html):
        """Strip out comments, scripts, styles, meta
        from the html, as well as element attrs. For details see
        http://lxml.de/api/lxml.html.clean.Cleaner-class.html"""

        cleaner = Cleaner(style=True, safe_attrs_only=True,
                          page_structure=False, safe_attrs=[])
        # strip non ascii chars
        html = filter(lambda x: ord(x) < 128, html)
        return cleaner.clean_html(html)
