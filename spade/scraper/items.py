# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class MarkupItem(Item):
    content_type = Field()
    filename = Field()
    headers = Field()
    meta = Field()
    raw_content = Field()
    sitescan = Field()
    url = Field()
    user_agent = Field()
