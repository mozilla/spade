# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from django.core.files.base import ContentFile


from scrapy.exceptions import DropItem
import spade.model.models as models
from urlparse import urljoin, urlparse

class ScraperPipeline(object):
    def process_item(self, item, spider):
        item_domain = urlparse(item['url']).netloc

        # Find the foreign keys they belong to, if they exist
        sitescan = models.SiteScan.objects.filter(site_url=item_domain)[:1]
        urlscan = models.URLScan.objects.filter(page_url=item['url'])[:1]

        # Generate appropriate site and url scans as needed
        if not sitescan:
            sitescan = models.SiteScan()
            sitescan.batch = spider.batch
            sitescan.site_url = item_domain
            sitescan.save()
        else:
            sitescan = sitescan[0]

        if not urlscan:
            urlscan = models.URLScan()
            urlscan.site_scan = sitescan
            urlscan.page_url = item['url']
            urlscan.timestamp = spider.get_now_time()
            urlscan.save()
        else:
            urlscan = urlscan[0]

        # Javascript MIME types
        js_mimes = ('text/javascript',
                    'application/x-javascript',
                    'application/javascript')

        # Parse each file based on what its MIME specifies
        if 'text/html' in item['headers']:
            # First save the request contents into a URLContent
            urlcontent = models.URLContent()
            urlcontent.url_scan = urlscan
            urlcontent.user_agent = item['user_agent']

            # Store raw markup
            file_content = ContentFile(item['raw_markup'])
            urlcontent.raw_markup.save(item['filename'],file_content)
            urlcontent.raw_markup.close()

            # Store raw headers
            file_content = ContentFile(item['headers'])
            urlcontent.headers.save(item['filename'],file_content)
            urlcontent.headers.close()

            urlcontent.save()

        elif any(mime in item['headers'] for mime in js_mimes):
            linkedjs = models.LinkedJS()
            linkedjs.url_scan = urlscan

            # Store raw js
            file_content = ContentFile(item['raw_markup'])
            linkedjs.raw_js.save(item['filename'],file_content)
            linkedjs.raw_js.close()

            linkedjs.save()

        elif 'text/css' in item['headers']:
            linkedcss = models.LinkedCSS()
            linkedcss.url_scan = urlscan

            # Store raw css
            file_content = ContentFile(item['raw_markup'])
            linkedcss.raw_css.save(item['filename'],file_content)
            linkedcss.raw_css.close()

            linkedcss.save()

        # Update batch finish time, keep this last
        spider.batch.finish_time = spider.get_now_time()
        spider.batch.save()

        return item
