import re
from django.conf import settings
from ecs.tracking.models import Request, View

HTML_TITLE_RE = re.compile('<title>([^<]*)</title>', re.IGNORECASE)
HTML_TITLE_MAX_OFFSET = 1000

class TrackingMiddleware(object):
    def process_view(self, request, view, args, kwargs):
        if request.is_ajax() or \
            request.path.startswith(settings.STATIC_URL):
            request.tracking_data = None
        else:
            view, created = View.objects.get_or_create_for_url(request.path)
            kwargs = {
                'url': request.path,
                'method': request.method,
                'ip': request.META['REMOTE_ADDR'],
                'view': view,
            }
            if not request.user.is_anonymous():
                kwargs['user'] = request.user
            request.tracking_data = Request(**kwargs)
        
    def process_response(self, request, response):
        if not getattr(settings, 'ECS_TRACKING_ENABLED', False) or not getattr(request, 'tracking_data', None) or request.tracking_data.user is None:
            return response
        
        ct = response['Content-Type']
        request.tracking_data.content_type = ct

        if not request.tracking_data.title and ct.startswith('text/html'):
            match = HTML_TITLE_RE.search(response.content[:HTML_TITLE_MAX_OFFSET])
            if match:
                request.tracking_data.title = match.group(1)
        
        request.tracking_data.save()
        return response
