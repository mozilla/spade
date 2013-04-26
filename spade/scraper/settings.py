# Scrapy settings for scraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

# Allow scrapy to access django models
import os

# Allow scrapy to use "DjangoItem" (beta)
os.environ['DJANGO_SETTINGS_MODULE'] = 'spade.settings'
from django.conf import settings

SPIDER_MODULES = ['spade.scraper.spiders']
NEWSPIDER_MODULE = 'spade.scraper.spiders'

ITEM_PIPELINES = ['spade.scraper.pipelines.ScraperPipeline']

# Disable default user agent middleware
DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
}

# Disable the default filtering middleware and enable our own which only allows
# following internal links of a site (no offsite hyperlinks allowed!)
# Also disable depth middleware and replace with our own which only applies to
# HTML (not CSS or Javascripts)
SPIDER_MIDDLEWARES = {
    'scrapy.contrib.spidermiddleware.offsite.OffsiteMiddleware':None,
    'scrapy.contrib.spidermiddleware.depth.DepthMiddleware':None,
    'spade.scraper.middlewares.DepthMiddleware': 542,
    'spade.scraper.middlewares.OffsiteMiddleware': 543,
}

HTTPCACHE_ENABLED = True
HTTPCACHE_POLICY = 'scrapy.contrib.httpcache.RFC2616Policy'
# download cache expires every 4 hours
HTTPCACHE_EXPIRATION_SECS = 60 * 60 * 4
HTTPCACHE_DIR = os.path.join(settings.BASE_PATH, 'webcache')
HTTPCACHE_STORAGE = 'scrapy.contrib.downloadermiddleware.httpcache.FilesystemCacheStorage'
DEPTH_LIMIT = 2

DOWNLOAD_DELAY =1
DOWNLOAD_TIMEOUT=15
CONCURRENT_REQUESTS = 500
CONCURRENT_REQUESTS_PER_DOMAIN = 16
LOG_LEVEL='INFO'
DEPTH_PRIORITY = 1

#Obey robots.txt
ROBOTSTXT_OBEY=True

DUPEFILTER_CLASS = "spade.scraper.dupefilter.MultipleUADupeFilter"
