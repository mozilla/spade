"""
Utility to parse and save CSS
"""
import cssutils
import logging
import os
from urllib import urlopen
from spade.model import models

# Ensure that warnings for CSS properties are disabled: cssutils throws
# warnings when properties are not recognized. It also only recognizes up to
# CSS2, and a few CSS3 properties. Most prefixed properties will cause warnings
# We're only using cssutils to iterate over rules, so this is fine
cssutils.log.setLevel(logging.FATAL)


class CSSParser(object):
    def __init__(self, raw_css):
        """ Initialize a cssutils parser """
        self.parse(raw_css)

    def parse(self, css):
        self.css = cssutils.parseString(css).cssRules

    def parse_rule(self, rule):
        """
        Returns a tuple containing the rule's selector and parsed properties
        Example: (selector, { property: (prefix, unprefixed_name, value), })
        """
        selector_string = " ".join([s.selectorText for s in rule.selectorList])

        # Get property strings
        properties = []
        for property in rule.style:
            properties.append((property.name, property.value))

        # Create the dictionary that gives us easy access to the components of
        # the property
        properties_dict = {}
        for (name, val) in properties:
            if name.startswith('-moz-'):
                unprefixed_name = name.split('-moz-')[1]
                properties_dict[name] = ('-moz-', unprefixed_name, val)
            elif name.startswith('-webkit-'):
                unprefixed_name = name.split('-webkit-')[1]
                properties_dict[name] = ('-webkit-', unprefixed_name, val)
            elif name.startswith('-ms-'):
                unprefixed_name = name.split('-ms-')[1]
                properties_dict[name] = ('-ms-', unprefixed_name, val)
            else:
                # The name is already unprefixed
                properties_dict[name] = ("", name, val)

        return (selector_string, properties_dict)

    def get_selector_list(self):
        """ Retrieve CSS selectors """
        selectors = []
        for rule in self.css:
            selectors.append(rule.selectorText)
        return selectors

    def is_comment(self, rule):
        """ Returns whether a rule a comment """
        return rule.typeString == "COMMENT"

    def store_css(self, sitescan):
        """
        Calls parse on the internal CSS, stores css properties into db model
        """
        for rule in self.css:
            if self.is_comment(rule):
                # Ignore Comments
                continue

            # Get selector and properties from rule
            rule = self.parse_rule(rule)
            selector = rule[0]
            properties = rule[1]

            # Create CSS rule in model
            current_rule = models.CSSRule.objects.create(sitescan=sitescan,
                                                         selector=selector)

            for property in properties:
                prefix = properties[property][0]
                unprefixed_name = properties[property][1]
                value = properties[property][2]

                # Create CSSProperty object for each property belonging to the
                # rule
                new_property = models.CSSProperty.objects.create(
                    rule=current_rule, prefix=prefix, name=unprefixed_name,
                    value=value)

        return True
