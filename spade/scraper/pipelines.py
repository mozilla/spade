# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from django.core.files.base import ContentFile
from scrapy.exceptions import DropItem
from urlparse import urljoin, urlparse

import spade.model.models as models

class ScraperPipeline(object):
    def process_item(self, item, spider):
        """Called whenever an item is yielded by the spider"""
        item_domain = urlparse(item['url']).netloc

        # Find the foreign keys they belong to, if they exist
        sitescan = models.SiteScan.objects.filter(batch=spider.batch,
                                                  site_url=item_domain)

        # Generate appropriate site and url scans as needed
        # TODO: DEAL WITH RACE CONDITIONS
        if not sitescan:
            sitescan = models.SiteScan.objects.create(batch=spider.batch,
                                       site_url=item_domain)
        else:
            sitescan = sitescan[0]

        urlscan = models.URLScan.objects.filter(site_scan = sitescan,
                                                page_url=item['url'])

        if not urlscan:
            urlscan = models.URLScan.objects.create(site_scan=sitescan,
                                     page_url=item['url'],
                                     timestamp=spider.get_now_time())
        else:
            urlscan = urlscan[0]

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

