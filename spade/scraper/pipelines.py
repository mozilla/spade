# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

class ScraperPipeline(object):
    def open_spider(spider):
        pass
        # open batch

    def close_spider(spider):
        pass
        # close batch

    def process_item(self, item, spider):
        return item
