from spade.scraper.spiders.general_spider import GeneralSpider
from scrapy.conf import settings

def pytest_funcarg__spider(request):
    settings.overrides['LOG_ENABLED'] = True
    settings.overrides['URLS'] = "sitelists/test.txt"
    return GeneralSpider()

def test_name(spider):
    assert spider.name == "all"
