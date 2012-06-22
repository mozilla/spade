# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

# TODO: This will eventually be removed in favor of our django models
class GeneralItem(Item):
    url = Field()
    #status_code = Field()
    #body = Field()
    #headers = Field()
    #content_type = Field()
    #md5sum_body = Field()
    #referrer = Field()
    #user_agent = Field()
