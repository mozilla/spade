from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from android.items import TopsitesItem
from scrapy.http import Request
from scrapy import log

import time
import urlparse
import hashlib
import MySQLdb
import cPickle as pickle
import json
import zlib
import random

USER_AGENT = 'android'
SITE_LIST = '/data/moz/Mozilla/Projects/Scrapy/topsites.txt'

'''
CREATE TABLE android
 (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
 url TEXT,
 timestamp INT NOT NULL,
 referrer TEXT,
 content_type TEXT,
 gzheaders MEDIUMBLOB,
 gzbody MEDIUMBLOB);

'''


def queue_log(url):
    pass #info('Adding to the queue: %s' % url)

def info(msg):
    log.msg(msg, level=log.INFO)

def get_allowed_domains():
    return [urlparse.urlsplit(d)[1] for d in get_start_urls()]

def get_start_urls():
    data = open(SITE_LIST).read().strip().split()
    urls = [u for u in data if len(u) >= 7]
    random.shuffle(urls)
    return urls

def gzipped_json(obj):
    s = json.dumps(obj, ensure_ascii=False)
    return zlib.compress(s)

class AndroidSpider(BaseSpider):
    name = USER_AGENT
    allowed_domains = get_allowed_domains()
    start_urls = get_start_urls()
    
    def __init__(self):
        self.conn = MySQLdb.connect(host='localhost',user='scrapy',passwd='scrapy',db='scrapy')
        self.conn.set_character_set('utf8')
        self.cursor = self.conn.cursor()
        self.cursor.execute('SET NAMES utf8;')
        self.cursor.execute('SET CHARACTER SET utf8;')
        self.cursor.execute('SET character_set_connection=utf8;')
    
    def save(self, r):
        s = pickle.dumps(r)
        now = time.time()
        url = r['url']
        content_type = r['content_type']
        referrer = r['referrer']
        gzheaders = gzipped_json(r['headers'])
        gzbody = gzipped_json(r['body'])
        sql = 'INSERT INTO %s (url, timestamp, referrer, content_type, gzheaders, gzbody) VALUES ' % USER_AGENT
        sql = sql + '(%s, %s, %s, %s, %s, %s)'
        self.cursor.execute(sql, (url, now, referrer, content_type, gzheaders, gzbody))

    def get_content_type(self, headers):
        if headers:
            for h in headers:
                if h.lower().strip() == 'content-type':
                    return headers[h]
                    
    def desired_content_type(self, ct):
        '''right now we are only interested in html, javascript, and css'''
        
        if not ct:
            return False
        elif 'text/html' in ct:
            return True
        elif 'application/x-javascript' in ct:
            return True
        elif 'text/css' in ct:
            return True
        elif 'text/javascript' in ct:
            return True
        elif 'application/javascript' in ct:
            return True
        else:
            return False   
    
    def parse(self, response):
        r = TopsitesItem()
        r['url'] = response.url
        r['status_code'] = response.status
        r['body'] = response.body
        r['headers'] = response.headers
        r['content_type'] = self.get_content_type(response.headers)
        r['md5sum_body'] = hashlib.md5(r['body']).hexdigest()
        r['referrer'] = response.meta.get('referrer')
        r['user_agent'] = USER_AGENT
        
        if self.desired_content_type(r['content_type']):
            self.save(r)

        if 'text/html' in r['content_type']:
            hxs = HtmlXPathSelector(response)
            for url in hxs.select('//link/@href').extract() + \
                hxs.select('//script/@src').extract() + \
                hxs.select('//a/@href').extract():
    
                if not url.startswith('http://'):
                    if url.startswith('javascript:'):
                        continue 
                    else:
                        url = urlparse.urljoin(response.url,url)
                queue_log(url)
                request = Request(url, callback=self.parse)
                request.meta['referrer'] = response.url
                yield request
        
