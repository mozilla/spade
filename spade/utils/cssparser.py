"""
Utility to parse and save CSS
"""
import cssutils
import logging
from urllib import urlopen
from spade.model import models

# Ensure that warnings for CSS properties are disabled: cssutils throws
# warnings when properties are not recognized. It also only recognizes up to
# CSS2, and a few CSS3 properties. Most prefixed properties will cause warnings
cssutils.log.setLevel(logging.FATAL)


class CSSParser(object):
    def __init__(self, raw_css, sitescan=None):
        """ Initialize a cssutils parser """
        self.css = cssutils.parseString(raw_css).cssRules
        self.sitescan = sitescan

    def get_properties(self, rule):
        """
        Returns dictionary of properties and their values & prefixes from rule
        """
        selector_string = ""
        for selector in rule.selectorList:
            selector_string = selector_string + selector.selectorText

        # Get property strings
        split_rule = rule.cssText.split('{')
        split_rule = split_rule[1].split('}')
        property_strings = split_rule[0].split(';')

        # Separate property names from values
        property_tuples = []
        for data_string in property_strings:
            prop = data_string.split(':')
            property_tuples.append((prop[0], prop[1]))

        # Create tuples which contain prefixes and values & map these to props
        property_dict = {}
        for property_tuple in property_tuples:
            prop = property_tuple[0].strip()
            val = property_tuple[1]
            if '-moz-' in prop:
                prop = prop.split('-moz-')[1]
                property_dict[prop] = ('-moz-', val)
            elif '-webkit-' in prop:
                prop = prop.split('-webkit-')[1]
                property_dict[prop] = ('-webkit-', val)
            elif '-ms-' in prop:
                prop = prop.split('-ms-')[1]
                property_dict[prop] = ('-ms-', val)
            else:
                property_dict[prop] = ("", val)

        return {selector_string: property_dict}

    def get_selector_list(self):
        """ Retrieve CSS selectors """
        selectors = []
        for rule in self.css:
            selectors.append(rule.selectorText)
        return selectors

    def is_comment(self, rule):
        """ Returns whether a rule a comment """
        return rule.typeString == "COMMENT"

    def store(self, sitescan):
        """
        Calls parse on the internal CSS, stores css properties into db model
        """
        for rule in self.css:
            if self.is_comment(rule):
                # Ignore Comments
                continue

            # Get properties from rule
            properties = self.get_properties(rule)
            for key in properties.keys():
                selector = key

            # Create CSS rule in model
            current_rule = models.CSSRule(sitescan=sitescan, selector=selector)
            current_rule.save()

            for property_name in properties[selector]:
                property_prefix = properties[selector][property_name][0].strip()
                property_value = properties[selector][property_name][1].strip()

                # Create CSSProperty object for each property
                new_property = models.CSSProperty(rule=current_rule)
                new_property.prefix = property_prefix
                new_property.name = property_name
                new_property.value = property_value
                new_property.save()

        return True