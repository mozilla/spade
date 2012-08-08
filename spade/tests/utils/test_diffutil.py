"""
Tests for html diff util
"""
from spade.utils import htmldiff


def test_strip_basic():
    """Strip function should remove text between tags"""
    diff_util = htmldiff.HTMLDiff()
    html = u"<html><body><p>something</p></body></html>"

    stripped_html = diff_util.strip(html)

    # LXML's benefit is that it works on broken HTML by attempting to add back
    # things that should exist but don't (e.g head, docstring, body). As a
    # result the strip utility that we call on each page will add a docstring
    assert stripped_html == (u"""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0"""
    u""" Transitional//EN" """
    u""""http://www.w3.org/TR/REC-html40/loose.dtd">\n"""
    u"""<html><body><p></p></body></html>""")


def test_strip_complex():
    """Strip should handle nested content"""
    diff_util = htmldiff.HTMLDiff()
    html = (u"""<html><head><title>Test</title></head><body>Content<div>"""
    u"""More Content<div>Even more content</div>"""
    u"""</div></body></html>""")

    stripped_html = diff_util.strip(html)

    assert stripped_html == (u"""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0"""
    u""" Transitional//EN" """
    u""""http://www.w3.org/TR/REC-html40/loose.dtd">\n"""
    u"""<html><head><title></title>"""
    u"""</head><body><div><div></div></div></body></html>""")


def test_diff_same():
    """
    Diff utility should return 1 when two markups are the same
    """
    diff_util = htmldiff.HTMLDiff()
    html1 = u"<html><head></head><body></body></html>"
    html2 = u"<html><head></head><body></body></html>"

    similarity = diff_util.compare(html1, html2)

    assert similarity == 1


def test_diff_attrs():
    """In a diff, the attrs don't matter"""
    diff_util = htmldiff.HTMLDiff()
    html1 = u"""<html><body><div class="whatever"></div></body></html>"""
    html2 = u"""<html><body><div></div></body></html>"""

    similarity = diff_util.compare(html1, html2)

    assert similarity == 1

def test_diff_different():
    """
    Diff utility should see that one uses flat structure and the other uses
    nested which means they're not very similar.
    """
    diff_util = htmldiff.HTMLDiff()

    html1 = (u"""<html>"""
    u"""<head>"""
    u"""<title>This text should not matter</title>"""
    u"""</head>"""
    u"""<body>"""
    u"""    <div class="whatever">Testing 1 2 3</div>"""
    u"""    <div class="whatever">Another Test</div>"""
    u"""    <div class="whatever">Another Test</div>"""
    u"""</body>"""
    u"""</html>""")

    html2 =(u"""<html>"""
    u"""<head>"""
    u"""    <title>Differences are not important</title>"""
    u"""</head>"""
    u"""<body>"""
    u"""    <div class="hey">Markup structure"""
    u"""        <div class="whatever">is being"""
    u"""            <div class="whatever">tested</div>"""
    u"""        </div>"""
    u"""    </div>"""
    u"""</body>"""
    u"""</html>""")

    similarity = diff_util.compare(html1, html2)
    assert similarity < 0.9
