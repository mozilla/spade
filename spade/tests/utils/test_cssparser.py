"""
Tests for css parsing util
"""
from spade.utils import cssparser
from spade.model import models

from spade.tests.model.factories import LinkedCSSFactory

RAW_CSS = (u"html body{\n"
           u"color:#000;\n"
           u"margin:0 auto;\n"
           u"-moz-box-shadow: 10px 10px 5px #888;\n"
           u"font-size:10px\n}"
           u"a:visited a:hover{\n"
           u"color:#000;\n"
           u"-moz-box-shadow: 10px 10px 5px #888;\n"
           u"-webkit-something: something else\n}")


def pytest_funcarg__parser(request):
    return cssparser.CSSParser(RAW_CSS)


def test_arbitrary_prefix(parser):
    """ Make sure that unknown prefixes get saved """
    test_css = (u"body{\n"
                u"-testing-testprop: testval\n}")
    parser.parse(test_css)

    linkedcss = LinkedCSSFactory.create(raw_css=test_css)
    parser.store_css(linkedcss)

    find_property = models.CSSProperty.objects.filter(prefix="-testing-",
                                                      name="testprop",
                                                      value="testval")
    assert find_property.count() == 1


def test_unknown_property(parser):
    """ Make sure that unknown properties get saved """
    linkedcss = LinkedCSSFactory.create(raw_css=RAW_CSS)
    parser.store_css(linkedcss)

    find_property = models.CSSProperty.objects.filter(prefix="-webkit-",
                                                      name="something",
                                                      value="something else")
    assert find_property.count() == 1


def test_extract_rules(parser):
    """Make sure we get all rules supplied in CSS"""
    # Check to see that we have the correct selectors
    selectors = parser.get_selector_list()
    assert set(selectors) == set([u"html body", u"a:visited a:hover"])


def test_store_css(parser):
    """Make sure CSS rules are saved correctly"""
    linkedcss = LinkedCSSFactory.create(raw_css=RAW_CSS)
    parser.store_css(linkedcss)

    # The rule for "html body" should be saved
    find_rule = models.CSSRule.objects.filter(linkedcss=linkedcss,
                                              selector="html body")
    assert find_rule.count() == 1

    # The property "margin" should have been saved with value "0 auto"
    find_property = models.CSSProperty.objects.filter(rule=find_rule,
                                                      prefix="",
                                                      name="margin",
                                                      value="0 auto")
    assert find_property.count() == 1


def test_store_prefixed_properties(parser):
    """
    Ensure that when the same rule has both prefixed and unprefixed versions of
    the same property, the CSS is stored correctly
    """
    css = (u"html body{\n"
           u"box-shadow: 10px 10px 5px #888;\n}"
           u"a:visited a:hover{\n"
           u"-moz-box-shadow: 10px 10px 5px #000;\n}")
    parser.parse(css)

    linkedcss = LinkedCSSFactory.create(raw_css=css)
    parser.store_css(linkedcss)

    # Check to see that we saved the prefixed property -moz-box-shadow
    prefixed_property = models.CSSProperty.objects.filter(prefix="-moz-",
                                                          name="box-shadow",
                                                          value="10px 10px 5px #000")
    assert prefixed_property.count() == 1

    # Check to see that we saved the unprefixed property box-shadow
    unprefixed_property = models.CSSProperty.objects.filter(prefix="",
                                                            name="box-shadow",
                                                            value="10px 10px 5px #888")
    assert unprefixed_property.count() == 1

    # Make sure that the two properties are not the same object
    assert prefixed_property != unprefixed_property


def test_comments_dont_break_parser(parser):
    """
    Ensure comments between properties and rules don't break our parsing of CSS
    """
    # Place comments between various elements to see that they're successfully
    # ignored by the parser
    commented_css = (u"html body{ /* comment inline */\n"
                     u"box-shadow: 10px 10px 5px #888;\n"
                     u"/* comment between properties */\n"
                     u"color: #000;\n}"
                     u"/* comment between rules */\n"
                     u"a:visited a:hover{\n"
                     u"-moz-box-shadow: 10px 10px 5px #000;"
                     "/* comment inline */\n}")
    parser.parse(commented_css)

    linkedcss = LinkedCSSFactory.create(raw_css=commented_css)
    parser.store_css(linkedcss)

    # Check to see that expected rules were saved
    rule1 = models.CSSRule.objects.filter(linkedcss=linkedcss,
                                          selector="html body")

    assert rule1.count() == 1

    rule2 = models.CSSRule.objects.filter(linkedcss=linkedcss,
                                          selector="a:visited a:hover")
    assert rule2.count() == 1

    # Check to see that expected properties were saved
    property1 = models.CSSProperty.objects.filter(rule=rule1,
                                                  prefix="",
                                                  name="box-shadow",
                                                  value="10px 10px 5px #888")
    assert property1.count() == 1

    property2 = models.CSSProperty.objects.filter(rule=rule2,
                                                  prefix="-moz-",
                                                  name="box-shadow",
                                                  value="10px 10px 5px #000")
    assert property2.count() == 1
