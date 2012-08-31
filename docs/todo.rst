TODO
====

Add support for detecting CSS prefixing issues
----------------------------------------------

The ``DataAggregator`` attempts to detect UA-sniffing issues (by comparing
markup structures returned from the same URL for different UAs), but it does
not attempt to detect prefixed-CSS issues. The data needed for this detection
is all present in the database in the ``CSSRule`` and ``CSSProperty`` models,
but there is no code yet to iterate over those models and look for cases where
a non-mozilla prefixed property is used without the moz-prefixed or unprefixed
equivalent.


Evaluate adequacy of UA-sniffing-detection method
-------------------------------------------------

The scraper follows this algorithm when scraping:

1. Given a top-level URL from the URLs file, issue a request to that URL with
   each configured user-agent string.

2. From that point on, each user agent effectively crawls the site separately,
   following the links found in the pages delivered to that user agent.

This gives an accurate picture of the site as each user agent would really see
it (which is good for the CSS prefix checking), but in case of redirection to
separate mobile sites, it means that there may be very few (or no) URLs on the
site that are scraped in common by all user agents. The current form of
UA-sniffing detection (looking at markup returned to different UAs for the same
URL) is only effective if a site has at least one URL that returned actual
content to all user agents. It may be necessary to add more sophisticated
UA-sniffing detection code that accounts for different redirects received by
different user agents as well.


Integrate South for schema and data migrations
----------------------------------------------

At the moment, since Spade (including the database schema) is still under heavy
development, it's often easiest after a model change to simply drop and
recreate the database and run syncdb again, rather than worrying about how to
structure a migration for existing data.

At some point, Spade will be deployed into production and begin collecting
non-throwaway data. Before that happens, `South`_ should be integrated so that
future model changes can incorporate migrations to alter the schema and migrate
data as needed.

.. _South: http://south.aeracode.org


Complete the UI
---------------

The views in ``spade/view/views.py`` and the Django templates in ``spade/view/templates`` are incomplete, and need to be finished.
