"""
Test LinkedCSS and LinkedJS models
"""
from . import factories


def test_css_unicode(linkedcss):
    linkedcss = factories.LinkedCSSFactory()
    assert unicode(linkedcss) == u"body{color:#000}"


def test_js_unicode(linkedjs):
    linkedjs = factories.LinkedJSFactory()
    assert unicode(linkedjs) == u"document.write('hello world')"
