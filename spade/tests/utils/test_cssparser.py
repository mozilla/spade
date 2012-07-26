"""
Tests for css parsing util
"""
from spade.utils import cssparser
from spade.model import models

from spade.tests.model.factories import SiteScanFactory, CSSRuleFactory, CSSPropertyFactory


def pytest_funcarg__parser(request):
    css = "html body{\n"\
        "color:#000;\n"\
        "margin:0 auto;\n"\
        "-moz-box-shadow: 10px 10px 5px #888;\n"\
        "font-size:10px\n}"\
        "a:visited a:hover{\n"\
        "color:#000;\n"\
        "-moz-box-shadow: 10px 10px 5px #888;\n"\
        "-webkit-something: something else\n}"
    return cssparser.CSSParser(css)


def test_store_css(parser):
    """Make sure CSS rules are saved correctly"""
    sitescan = SiteScanFactory.create(site_url_hash="testhash",
                                      site_url="http://test.com")
    sitescan.save()
    parser.store(sitescan)

    find_rule, r_created = models.CSSRule.objects.get_or_create(sitescan=sitescan,
                                                                selector="html body")
    assert r_created == False

    find_property, p_created = models.CSSProperty.objects.get_or_create(rule=find_rule,
                                                                        prefix="-moz-",
                                                                        name="box-shadow",
                                                                        value="10px 10px 5px #888")
    assert p_created == False


def test_extract_rules(parser):
    """Make sure we get all rules supplied in CSS"""
    # Check to see that we have the correct selectors
    selectors = parser.get_selector_list()
    assert set(selectors) == set(["html body", "a:visited a:hover"])


def test_extract_properties(parser):
    """Make sure we get the correct properties from CSS"""
    # Check to see that the correct properties were parsed
    props = []
    for rule in parser.css:
        property_dict = parser.get_properties(rule)
        for key in property_dict.keys():
            selector = key
        for prop in property_dict[selector]:
            props.append(prop)

    real_props = ["color", "margin", "box-shadow", "font-size", "something"]
    assert set(props) == set(real_props)
