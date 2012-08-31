"""
Test LinkedCSS and LinkedJS models
"""
from . import factories


def test_css_unicode():
    linkedcss = factories.LinkedCSSFactory()
    assert unicode(linkedcss) == u"http://example.com/test.css"


def test_js_unicode():
    linkedjs = factories.LinkedJSFactory()
    assert unicode(linkedjs) == u"http://example.com/test.js"
