"""
Utility to parse and save CSS
"""
import cssutils
import logging
import re

from spade import model

# Ensure that warnings for CSS properties are disabled: cssutils throws
# warnings when properties are not recognized. It also only recognizes up to
# CSS2, and a few CSS3 properties. Most prefixed properties will cause warnings
# We're only using cssutils to iterate over rules, so this is fine
cssutils.log.setLevel(logging.FATAL)


class CSSParser(object):
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
        regex = re.compile("^-[a-zA-Z]+\-")
        for (name, val) in properties:
            result = regex.match(name)
            if result:
                prefix = result.group()
                unprefixed_name = name.split(prefix)[1]
                properties_dict[name] = (prefix, unprefixed_name, val)
            else:
                # The name is already unprefixed
                properties_dict[name] = ("", name, val)

        return (selector_string, properties_dict)


    def parse(self, linkedcss):
        """
        Calls parse on the internal CSS, stores css properties into db model
        """
        css = linkedcss.raw_css.read()
        for rule in cssutils.parseString(css).cssRules.rulesOfType(
                cssutils.css.CSSRule.STYLE_RULE):
            # Get selector and properties from rule
            rule = self.parse_rule(rule)
            selector = rule[0]
            properties = rule[1]

            # Create CSS rule in model
            current_rule = model.CSSRule.objects.create(linkedcss=linkedcss,
                                                         selector=selector)

            for property in properties:
                prefix = properties[property][0]
                unprefixed_name = properties[property][1]
                value = properties[property][2]

                # Create CSSProperty object for each property belonging to the
                # rule
                model.CSSProperty.objects.create(
                    rule=current_rule, prefix=prefix, name=unprefixed_name,
                    value=value)

        return True
