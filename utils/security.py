from functools import wraps
import threading
import logging
from django.db.models.signals import post_save, post_delete

logger = logging.getLogger(__name__)

def readonly(methods=('GET', 'POST')):
    def decorator(view):
        view._readonly_methods = methods
        return view
    return decorator


IGNORABLE_MODULES = ('ecs.audit.models', 'sentry.models')

def fqn(obj):
    return "%s.%s" % (obj.__module__, obj.__name__)

class SecurityReviewMiddleware(threading.local):
    def __init__(self):
        self._current_view = None
        
    def _is_readonly(self):
        if not self._current_view:
            return False
        methods = getattr(self._current_view, '_readonly_methods', ())
        return self._current_request.method in methods

    def _post_save(self, sender, **kwargs):
        if self._is_readonly():
            if sender.__module__ in IGNORABLE_MODULES:
                return
            logger.warn("readonly view %s used %s: %s" % (
                fqn(self._current_view), 
                'INSERT' if kwargs['created'] else 'UPDATE',
                kwargs['instance'],
            ))
        
    def _post_delete(self, sender, **kwargs):
        if self._is_readonly():
            if sender.__module__ in IGNORABLE_MODULES:
                return
            logger.warn("readonly view %s used DELETE %s" % (
                fqn(self._current_view),
                kwargs['instance'],
            ))
        
    def _connect(self):
        if getattr(self, '_connected', False):
            return
        post_save.connect(self._post_save)
        post_delete.connect(self._post_delete)
        self._connected = True
    
    def process_view(self, request, view, args, kwargs):
        self._connect()
        self._current_view = view
        self._current_request = request
        
    def process_response(self, request, response):
        self._current_view = None
        return response
    