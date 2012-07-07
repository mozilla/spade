# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class MarkupItem(Item):
    url = Field()
    sitescan = Field()
    user_agent = Field()
    raw_content = Field()
    headers = Field()
    content_type = Field()
    filename = Field()
    meta = Field()
