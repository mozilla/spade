
# """
# Tests for html diff util
# """
from spade.utils import html_diff


def test_diff_same():
    """
    Diff utility should return 1 when two markups are the same
    """
    diff_util = html_diff.HTMLDiff()
    html1 = u"<html><head></head><body></body></html>"
    html2 = u"<html><head></head><body></body></html>"

    similarity = diff_util.compare(html1, html2)

    assert similarity == 1


def test_strip_unicode():
    """HTMLDiff.strip should strip out ascii-incompatible characters"""
    differ = html_diff.HTMLDiff()
    funny_html = (u"<html><head></head><body>"
                  u"These chars are really funny:¼ õ</body></html>")
    ascii_only = (u"<html><head></head><body>"
                  u"These chars are really funny: </body></html>")
    assert differ.strip(funny_html) == ascii_only


def test_strip_clean_hmtl():
    differ = html_diff.HTMLDiff()
    funny_html = (u"<html><head><script>alert('Delete me!')</script></head><body>"
                  u"<p><a href=\"/go-there\">go there</a></p></body></html>")
    clean_html = (u"<html><head></head><body>"
                  u"<p><a>go there</a></p></body></html>")
    assert differ.strip(funny_html) == clean_html
