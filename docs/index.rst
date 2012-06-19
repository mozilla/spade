.. Spade documentation master file, created by
   sphinx-quickstart on Mon Jun 18 15:39:03 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Spade's documentation!
=================================

**Overview:** Spade is at its core a metrics tool that allows quick visualization of
what kinds of CSS properties websites are using. It allows input of
a list of websites to scrape, and it crawls to 1 level on each website
whilst submitting a variety of user agent strings in order to ascertain
different kinds of markup returned as a result. It tries to detect UA
sniffing by commparing the returned markup structure of each site.

All the information is recorded into a database after the crawl, and
is accessible from a web interface. For more information on installation
and use of the tool, please continue through the documentation.

Contents:

.. toctree::
   :maxdepth: 2

   installation
   howto
   architecture



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

