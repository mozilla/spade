Architecture
============

The primary components are listed below (by Python module path) and described:

``spade.controller.management.commands``
----------------------------------------

Contains the ``scrape`` and ``useragents`` management commands.

``spade.model.models``
----------------------

Contains the database models:

A ``UserAgent`` stores a user-agent string that will be used to scrape sites
the next time the ``scrape`` management command is run.

A ``Batch`` represents a single run of the ``scrape`` management command.

A ``BatchUserAgent`` stores a user-agent string that actually was used when
scraping a particular batch. This is copied from a ``UserAgent`` when
``scrape`` is run; the separation prevents future changes to the user-agent
list from modifying or corrupting data from past runs.

A ``SiteScan`` object is created for each top-level URL in the list of URLs
given to the ``scrape`` management command.

A ``URLScan`` object is created for each URL scanned; this includes the initial
top-level URLs, and all linked pages one level deep.

A ``URLContent`` object stores the scraped contents of a single URL for a
particular user agent. In other words, for every ``URLScan`` there will be N
``URLContent`` objects, if there are N ``UserAgent`` records at the time the
scrape is initiated.

A ``LinkedCSS`` contains information about a single linked CSS file. Every CSS
file at a distinct URL has only one ``LinkedCSS`` record, even if it was linked
from multiple scraped HTML pages (thus ``LinkedCSS`` has a many-to-many
relationship with ``URLContent``).

Similarly, a ``LinkedJS`` contains information about a single linked JS file.

When the contents of a ``LinkedCSS`` file are parsed by
``spade.utils.cssparser.CSSParser``, a ``CSSRule`` object is created for every
CSS rule in the file, and a ``CSSProperty`` object for every property in every
rule.

The various ``*Data`` models contain aggregated data about issues detected in
the scan.


``spade.scraper``
-----------------

A `Scrapy`_ scraper that :doc:`scrapes a list of given URLs<scraper>` with all
user-agent strings listed in the database, following links one level deep, and
saving all response contents (including linked JS and CSS) in the database.

.. _Scrapy: http://scrapy.org/


``spade.settings``
------------------

Contains the Django project settings.


``spade.tests``
---------------

Contains the tests.


``spade.utils.data_aggregator``
-------------------------------

Contains a ``DataAggregator`` class that populates the ``BatchData``,
``SiteScanData``, ``URLScanData``, ``URLContentData`` and ``LinkedCSSData``
models with summary aggregate data about the scan.


``spade.utils.css_parser``
--------------------------

Contains a ``CSSParser`` class that can take raw CSS, parse it, and store it
into the ``CSSRule`` and ``CSSProperty`` database models.


``spade.utils.html_diff``
-------------------------

Contains a ``HTMLDiff`` class that can compare the tag structure of two chunks
of HTML, ignoring differences in tag content and attributes, and return a
measure of their similarity (0.0 if they have nothing in common, 1.0 if they
are identical).


``spade.view.urls``
-------------------

The URL configuration for the site.

Run ``python manage.py runserver`` to fire up a development web server and view
the app in your browser at ``http://localhost:8000/``.


``spade.view.views``
--------------------

Contains the Django view functions.
