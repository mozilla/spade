"""
Item pipeline.

"""
from django.core.files.base import ContentFile
from hashlib import sha256, sha1

from spade import model
from spade.utils.cssparser import CSSParser


class ScraperPipeline(object):
    def __init__(self):
        """Initialize pipeline."""
        self.css_parser = CSSParser()


    def process_item(self, item, spider):
        """Called whenever an item is yielded by the spider"""

        # strip non ascii chars
        item['raw_content'] = ''.join(c for c in item['raw_content'] if ord(c) < 128)

        # hash the filename to prevent storing too-long file names
        hash_data = item['filename'] + item['user_agent'].ua_string
        filename = sha1(hash_data).hexdigest()

        # Javascript MIME types
        js_mimes = ('text/javascript',
                    'application/x-javascript',
                    'application/javascript')

        # Parse each file based on what its MIME specifies
        if 'text/html' == item['content_type']:
            # First save the request contents into a URLContent
            urlcontent = model.URLContent.objects.create(
                url_scan=item['urlscan'],
                user_agent=item['user_agent'],
                redirected_from=item['redirected_from'])

            # Store raw markup
            file_content = ContentFile(item['raw_content'])
            urlcontent.raw_markup.save(filename, file_content)
            urlcontent.raw_markup.close()

            # Store raw headers
            file_content = ContentFile(item['headers'])
            urlcontent.headers.save(filename, file_content)
            urlcontent.headers.close()

            urlcontent.save()

        elif any(mime == item['content_type'] for mime in js_mimes):
            urlcontent = model.URLContent.objects.get(
                url_scan=item['urlscan'],
                user_agent=item['user_agent'])

            linkedjs, _ = model.LinkedJS.objects.get_or_create(
                batch=spider.batch,
                url_hash=sha256(item['url']).hexdigest(),
                defaults={'url': item['url']},
                )

            # Store raw js
            file_content = ContentFile(item['raw_content'])
            linkedjs.raw_js.save(filename, file_content)
            linkedjs.raw_js.close()

            linkedjs.save()

            # Create relationship with url content
            linkedjs.linked_from.add(urlcontent)

        elif 'text/css' == item['content_type']:
            urlcontent = model.URLContent.objects.get(
                url_scan=item['urlscan'],
                user_agent=item['user_agent'])

            linkedcss, created = model.LinkedCSS.objects.get_or_create(
                batch = spider.batch,
                url_hash=sha256(item['url']).hexdigest(),
                defaults={
                    'url': item['url'],
                    },
                )

            # Store raw css
            file_content = ContentFile(item['raw_content'])
            linkedcss.raw_css.save(filename, file_content)
            linkedcss.raw_css.close()

            linkedcss.save()

            # Create relationship with url content
            linkedcss.linked_from.add(urlcontent)

            if created:
                # Parse out rules and properties
                self.css_parser.parse(linkedcss)

        return item

    def close_spider(self, spider):
        """ Executed on spider completion """

        # Update batch finish time, keep this last
        spider.batch.finish_time = spider.get_now_time()
        spider.batch.save()

    def open_spider(self, spider):
        """ Executed on spider launch """
        now = spider.get_now_time()

        # Create initial batch
        spider.batch = model.Batch.objects.create(
            kickoff_time=now, finish_time=now)
        spider.batch.save()

        # save initial site list
        file_content = ContentFile('\n'.join(spider.start_urls))
        filename = str(spider.batch).replace(' ', '')
        spider.batch.sitelist.save(filename, file_content)
        spider.batch.sitelist.close()
        spider.batch.save()

        spider.batch_user_agents = []

        # Give the spider a set of batch user agents, which preserve historical
        # user agent data
        for ua in list(model.UserAgent.objects.all()):
            batch_user_agent = model.BatchUserAgent.objects.create(
                batch=spider.batch,
                ua_string=ua.ua_string,
                primary_ua=ua.primary_ua,
                ua_type=ua.ua_type,
                ua_human_name=ua.ua_human_name
                )
            spider.batch_user_agents.append(batch_user_agent)

        if not spider.batch_user_agents:
            raise ValueError(
                "No user agents; add some with 'manage.py useragents --add'")
