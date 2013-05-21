from scrapy.crawler import Crawler
from scrapy.utils.project import get_project_settings
from spade.scraper.spiders.general_spider import GeneralSpider
from spade import model


def pytest_funcarg__spider(request):
    """Use scrapy's overrides to start a spider w/ specific settings"""
    # This is necessary because the spider errors when a source file is not
    # provided.
    settings = get_project_settings()
    settings.overrides['URLS'] = u"spade/tests/sitelists/urls.txt"
    settings.overrides['LOG_ENABLED'] = True

    # Initialize and return spider

    spider = GeneralSpider()
    spider.set_crawler(Crawler(settings))
    now = spider.get_now_time()
    spider.batch = model.Batch.objects.create(
        kickoff_time=now, finish_time=now)
    spider.batch.save()

    # Delete created batch from database when test is done
    request.addfinalizer(lambda: spider.batch.delete())
    return spider
