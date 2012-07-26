"""
Tests for html diff util
"""
from spade.utils import htmldiff


def test_strip_basic():
    """Strip function should remove text between tags"""
    diff_util = htmldiff.HTMLDiff()
    html = u"<html><body><p>something</p></body></html>"

    stripped_html = diff_util.strip(html)

    assert stripped_html == u"""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0"""\
    """ Transitional//EN" """\
    u""""http://www.w3.org/TR/REC-html40/loose.dtd">\n"""\
    """<html><body><p></p></body></html>"""


def test_strip_complex():
    """Strip should handle nested content"""
    diff_util = htmldiff.HTMLDiff()
    html = u"""<html><head><title>Test</title></head><body>Content<div>"""\
    u"""More Content<div>Even more content</div>"""\
    u"""</div></body></html>"""

    stripped_html = diff_util.strip(html)

    assert stripped_html == u"""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0"""\
    """ Transitional//EN" """\
    """"http://www.w3.org/TR/REC-html40/loose.dtd">\n"""\
    u"""<html><head><title></title>""" \
    u"""</head><body><div><div></div></div></body></html>"""


def test_diff_same():
    """
    Diff utility should say two sites with different structure are different
    """
    diff_util = htmldiff.HTMLDiff()
    html1 = "<html><head></head><body></body></html>"
    html2 = "<html><head></head><body></body></html>"

    similarity = diff_util.compare(html1, html2)

    assert similarity == 1


def test_diff_attrs():
    """In a diff, the attrs don't matter"""
    diff_util = htmldiff.HTMLDiff()
    html1 = """<html><body><div class="whatever"></div></body></html>"""
    html2 = """<html><body><div></div></body></html>"""

    similarity = diff_util.compare(html1, html2)

    assert similarity == 1

def test_diff_different():
    """
    Diff utility should see that one uses flat structure and the other uses
    nested which means they're not very similar.
    """
    diff_util = htmldiff.HTMLDiff()

    html1 = """<html>
    <head>
        <title>What up dawg</title>
    </head>
    <body>
        <div class="whatever">HELLO</div>
        <div class="whatever">WHAT IS YOUR NAME</div>
        <div class="whatever">MINE IS SAM</div>
    </body>
    </html>
    """

    html2 ="""<html>
    <head>
        <title>What up dawg</title>
    </head>
    <body>
        <div class="hey">HELLO
            <div class="whatever">WHAT IS YOUR NAME
                <div class="whatever">MINE IS SAM</div>
            </div>
        </div>
    </body>
    </html>
    """

    similarity = diff_util.compare(html1, html2)
    assert 0 < similarity < 1.0
