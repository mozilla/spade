# Define middleware here

class PreRequestMiddleware(object):
    # This middleware allows us to define user agent
    # based on the django database

    def process_request(self, request, spider):
        if spider.user_agent:
            ua = spider.user_agent
            request.headers.setdefault('User-Agent', ua)
