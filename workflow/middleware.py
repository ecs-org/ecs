from ecs.workflow import registry

class WorkflowMiddleware(object):
    def process_request(self, request):
        registry._load()