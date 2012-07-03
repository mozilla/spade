# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from django.core.files.base import ContentFile


from scrapy.exceptions import DropItem
import spade.model.models as models

class ScraperPipeline(object):
    def process_item(self, item, spider):
        print "got item for "+ item['url']

        # TODO: Check if a sitescan exists. If not, create it. If so, set it to a var.
        # TODO: Check if a urlscan exists: if so, use it as a parent for each page. if not, create it with parent sitescan.

        ## Only create a sitescan object for each base site in the list
        #if response.meta.get('referrer') is None:
        #    # Take care not to generate
        #    curr_sitescan = models.SiteScan()
        #    curr_sitescan.batch = self.batch
        #    curr_sitescan.site_url = urlparse(response.url).netloc
        #    curr_sitescan.folder_name = urlparse(response.url).netloc
        #    curr_sitescan.save()
        #    print "new sitescan for " + urlparse(response.url).netloc

        ## Generate a urlscan for this url
        #curr_urlscan = models.URLScan()
        #curr_urlscan.site_scan = self.curr_sitescan
        #curr_urlscan.page_url = response.url
        #curr_urlscan.timestamp = self.get_now_time()
        #curr_urlscan.save()



        #js_mimes = ('text/javascript',
        #            'application/x-javascript',
        #            'application/javascript')

        #if 'text/html' in item['headers']:
        #    # First save the request contents into a URLContent
        #    urlcontent = models.URLContent()
        #    urlcontent.url_scan = item['url_scan']
        #    urlcontent.user_agent = item['user_agent']

        #    # Store raw markup
        #    file_content = ContentFile(item['raw_markup'])
        #    urlcontent.raw_markup.save(item['filename'],file_content)
        #    urlcontent.raw_markup.close()

        #    # Store raw headers
        #    file_content = ContentFile(item['headers'])
        #    urlcontent.headers.save(item['filename'],file_content)
        #    urlcontent.headers.close()

        #    urlcontent.save()

        #elif any(mime in item['headers'] for mime in js_mimes):
        #    linkedjs = models.LinkedJS()
        #    linkedjs.url_scan = item['url_scan']

        #    # Store raw js
        #    file_content = ContentFile(item['raw_markup'])
        #    linkedjs.raw_js.save(item['filename'],file_content)
        #    linkedjs.raw_js.close()

        #    linkedjs.save()

        #elif 'text/css' in item['headers']:
        #    linkedcss = models.LinkedCSS()
        #    linkedcss.url_scan = item['url_scan']

        #    # Store raw css
        #    file_content = ContentFile(item['raw_markup'])
        #    linkedcss.raw_css.save(item['filename'],file_content)
        #    linkedcss.raw_css.close()

        #    linkedcss.save()

        ## Update batch finish time, keep this last
        #spider.batch.finish_time = spider.get_now_time()
        #spider.batch.save()

        print item['meta']
        return item
