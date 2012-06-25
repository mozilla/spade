# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field
#from scrapy.contrib_exp.djangoitem import DjangoItem
#from spade.model.models import Batch, SiteScan, URLScan, URLContent, LinkedCSS, UserAgent

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

#class BatchItem(DjangoItem):
#    django_model = Batch
#
#class SiteScanItem(DjangoItem):
#    django_model = SiteScan
#
#class URLScanItem(DjangoItem):
#    django_model = URLScan
#
#class URLContentItem(DjangoItem):
#    django_model = URLContent
#
#class LinkedCSSItem(DjangoItem):
#    django_model = LinkedCSS
#
#class UserAgentItem(DjangoItem):
#    django_model = UserAgent
