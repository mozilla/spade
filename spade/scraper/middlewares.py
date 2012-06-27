from scrapy.http import Request
import spade.model.models as models

# Define middleware here
USER_AGENTS = models.UserAgent.objects.all()

class PreRequestMiddleware(object):
    # This middleware allows us to define user agent
    # based on the django database

    def process_request(self, request, spider):
        # meta is set by the spider, which distributes tasks with UA strings to us

        ua = spider.user_agent

        if request.meta.get('user_agent'):
            ua = request.meta['user_agent']

        request.headers.setdefault('User-Agent', ua)

        # Generate requests per user agent
        agent_index = request.meta.get('agent_index')
        if agent_index == None:
            agent_index = 0

            # Generate different UA responses
            while agent_index < len(USER_AGENTS):
                new_request = request.copy()
                new_request.headers.setdefault('User-Agent', USER_AGENTS[agent_index].ua_string)
                new_request.meta['agent_index'] = agent_index

                # Recurse
                agent_index = agent_index + 1
                self.process_request(new_request, spider)
