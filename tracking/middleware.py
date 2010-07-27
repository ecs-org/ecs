import re
from django.conf import settings
from ecs.tracking.models import Request

HTML_TITLE_RE = re.compile('<title>([^<]*)</title>', re.IGNORECASE)
HTML_TITLE_MAX_OFFSET = 1000

class TrackingMiddleware(object):
    def process_response(self, request, response):
        if request.user.is_anonymous():
            return response
        if request.path.startswith(settings.MEDIA_URL):
            return response
        ct = response['Content-Type']
        title = ""
        if ct.startswith('text/html'):
            match = HTML_TITLE_RE.search(response.content[:HTML_TITLE_MAX_OFFSET])
            if match:
                title = match.group(1)
            
        try:
            Request.objects.create(
                url=request.path,
                method=request.method,
                ip=request.META['REMOTE_ADDR'],
                user=request.user,
                content_type=ct,
                title=title
            )
        except Exception, e:
            raise
        
        return response