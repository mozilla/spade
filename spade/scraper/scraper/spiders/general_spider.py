# General spider for retrieving site information

from scrapy.spider import BaseSpider
import zlib
import json
import urlparse

USER_AGENT='android'

class GeneralSpider(BaseSpider):
    name = "dmoz"
    allowed_domains = ["dmoz.org"]
    start_urls = [
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Books/",
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/"
    ]

    # Get's a content type from the headers
    def get_content_type(self, headers):
        if headers:
            for h in headers:
                if h.lower().strip() == 'content-type':
                    return headers[h]

    # Gzip a json object for storage
    def gzipped_json(obj):
        s = json.dumps(obj, ensure_ascii=False)
        return zlib.compress(s)

    def parse(self, response):
        print response.url
        print response.body
        print response.headers
        print self.get_content_type(response.headers)
        print response.meta.get('referrer')
        print USER_AGENT
