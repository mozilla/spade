from scrapy.http import Request
import spade.model.models as models

# Define middleware here
USER_AGENTS = models.UserAgent.objects.all()

class PreRequestMiddleware(object):
    # This middleware allows us to define user agent
    # based on the django database

    def process_request(self, request, spider):
        # meta is set by the spider, which distributes tasks with UA strings to us
        if request.meta.get('user_agent'):
            spider.user_agent = request.meta['user_agent']

        if spider.user_agent:
            ua = spider.user_agent
            request.headers.setdefault('User-Agent', ua)
