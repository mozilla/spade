# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from django.core.files.base import ContentFile
from hashlib import sha256
from scrapy.exceptions import DropItem

import spade.model.models as models

class ScraperPipeline(object):
    def open_spider(spider):
        pass
        # open batch

    def close_spider(spider):
        pass
        # close batch

    def process_item(self, item, spider):
        """Called whenever an item is yielded by the spider"""

        sitescan, ss_created = models.SiteScan.objects.get_or_create(
                                   batch=spider.batch,
                                   site_url=item['sitescan'],
                                   site_hash=sha256(item['sitescan']).hexdigest(),
                               )

        urlscan, us_created = models.URLScan.objects.get_or_create(
                                  site_scan=sitescan,
                                  page_url=item['url'],
                                  defaults={'timestamp': spider.get_now_time()}
                              )


        # Javascript MIME types
        js_mimes = ('text/javascript',
                    'application/x-javascript',
                    'application/javascript')

        # Parse each file based on what its MIME specifies
        if 'text/html' in item['content_type']:
            # First save the request contents into a URLContent
            urlcontent = models.URLContent.objects.create(url_scan=urlscan,
                                           user_agent = item['user_agent'])

            # Store raw markup
            file_content = ContentFile(item['raw_content'])
            urlcontent.raw_markup.save(item['filename'],file_content)
            urlcontent.raw_markup.close()

            # Store raw headers
            file_content = ContentFile(item['headers'])
            urlcontent.headers.save(item['filename'],file_content)
            urlcontent.headers.close()

            urlcontent.save()

        elif any(mime in item['content_type'] for mime in js_mimes):
            linkedjs = models.LinkedJS.objects.create(url_scan=urlscan)

            # Store raw js
            file_content = ContentFile(item['raw_content'])
            linkedjs.raw_js.save(item['filename'],file_content)
            linkedjs.raw_js.close()

            linkedjs.save()

        elif 'text/css' in item['content_type']:
            linkedcss = models.LinkedCSS.objects.create(url_scan=urlscan)

            # Store raw css
            file_content = ContentFile(item['raw_content'])
            linkedcss.raw_css.save(item['filename'],file_content)
            linkedcss.raw_css.close()

            linkedcss.save()

        return item

    def close_spider(self, spider):
        """Executed on spider completion"""
        # Update batch finish time, keep this last
        spider.batch.finish_time = spider.get_now_time()
        spider.batch.save()

    def open_spider(self, spider):
        """Executed on spider launch"""
        now = spider.get_now_time()

        # Create initial batch
        spider.batch = models.Batch.objects.create(kickoff_time=now,
                                                   finish_time=now)
        spider.batch.save()

        # Get user agents from database and make them available to the spider
        spider.user_agents = models.UserAgent.objects.all()

