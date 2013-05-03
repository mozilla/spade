import os

from scrapy.contrib.downloadermiddleware.httpcache import FilesystemCacheStorage
from scrapy.utils.request import request_fingerprint


class SpadeFilesystemCacheStorage(FilesystemCacheStorage):
    def _get_request_path(self, spider, request):
        key = request_fingerprint(request, include_headers=['User-Agent'])
        return os.path.join(self.cachedir, spider.name, key[0:2], key)
