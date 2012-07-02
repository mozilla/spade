"""
Test LinkedCSS and LinkedJS models
"""
from . import factories

def pytest_funcarg__linkedcss(request):
    return factories.LinkedCSSFactory()

def pytest_funcarg__linkedjs(request):
    return factories.LinkedJSFactory()

def test_css_unicode(linkedcss):
    assert unicode(linkedcss) == u"body{color:#000}"

def test_js_unicode(linkedjs):
    assert unicode(linkedjs) == u"document.write('hello world')"
