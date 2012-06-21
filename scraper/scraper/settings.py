# Scrapy settings for scraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'scraper'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

# Allow scrapy to access django models
import os
import imp

# Allow scrapy to use "DjangoItem" (beta)
os.environ['DJANGO_SETTINGS_MODULE'] = 'spade.settings'


# Sets up django environment to allow scrapy to access django models
def setup_django_env(path):
    from django.core.management import setup_environ

    f, filename, desc = imp.find_module('settings', [path])
    project = imp.load_module('settings', f, filename, desc)

    setup_environ(project)

# Broke up the os.path calls to satisfy PEP8
this_path = os.path.abspath(__file__)
project_path = os.path.dirname(os.path.dirname(os.path.dirname(this_path)))
django_app = os.path.join(project_path, "spade")

setup_django_env(django_app)
