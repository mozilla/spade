Scraper
====================
Spade comes with a built-in scraper to crawl websites. It crawls all urls given
by a text file via command line args, as well as 1-level-deep links within each
site. It saves html, css, and javascript from the pages using whatever user
agents are specified in the database.

Using the scraper
-----------------
1. Add user agent strings that you would like to crawl with by running the
   management command. ::

    python manage.py useragents --add "Firefox / 5.0"

2. Call the scraper crawl all command, giving it a text file of URLs to parse. ::

    python manage.py scrape [newline delimited text file of URLS]
