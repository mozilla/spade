# Scrapy settings for scraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

# Allow scrapy to access django models
import os
import imp

BOT_NAME = 'scraper'
BOT_VERSION = '1.0'

# Allow scrapy to use "DjangoItem" (beta)
os.environ['DJANGO_SETTINGS_MODULE'] = 'spade.settings'

SPIDER_MODULES = ['spade.scraper.spiders']
NEWSPIDER_MODULE = 'spade.scraper.spiders'

ITEM_PIPELINES = ['spade.scraper.pipelines.ScraperPipeline']

# Disable default user agent middleware, swap in our custom one which uses all
# user agents listed in the database.
DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
}

# Disable the default filtering middleware and enable our own which only allows
# following internal links of a site (no offsite hyperlinks allowed!)
SPIDER_MIDDLEWARES = {
    'scrapy.contrib.spidermiddleware.offsite.OffsiteMiddleware':None,
    'spade.scraper.middlewares.CustomOffsiteMiddleware': 543,
}

# Based on our modifications, depth_limit is x+1 because we use level 0 to
# crawl the backbone of the site. Rescanning the same page with different user
# agents is considered level 1, and we want to go down to level 2 (which is
# really just 1 level deep).
DEPTH_LIMIT = 2

DOWNLOAD_DELAY = 0
DOWNLOAD_TIMEOUT=20
ENCODING_ALIASES = {'gb2312':'zh-cn', 'cp1251':'win-1251'}
CONCURRENT_REQUESTS = 64
CONCURRENT_REQUESTS_PER_DOMAIN = 16
LOG_LEVEL='INFO'
DEPTH_PRIORITY = 1

#Obey robots.txt
ROBOTSTXT_OBEY=True
