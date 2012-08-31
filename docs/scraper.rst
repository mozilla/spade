Scraper
====================
Spade comes with a built-in scraper to crawl websites. It crawls all urls given
by a text file via command line args, as well as 1-level-deep links within each
site. It saves html, css, and javascript from the pages using whatever user
agents are specified in the database.

Using the scraper
-----------------
1. Add user agent strings that you would like to crawl with by running the
   management command::

    python manage.py useragents --add "Firefox / 15.0" --desktop
    python manage.py useragents --add "Fennec / 15.0" --primary
    python manage.py useragents --add "Android / WebKit"

   Detecting UA-sniffing issues requires at least three user-agents to be
   added: a desktop user-agent to be used as baseline, a "primary" mobile user
   agent (the one we want to make sure sites are sniffing, if they sniff mobile
   UAs at all), and at least one other mobile UA to check against. A "UA
   sniffing issue" will be reported for a URL if that URL returns markedly
   different content for any non-primary mobile UA (compared to the desktop UA
   content), but returns the desktop content for the primary mobile UA.

2. Call the scrape command, giving it a text file of URLs to parse::

    python manage.py scrape [newline delimited text file of URLS]
