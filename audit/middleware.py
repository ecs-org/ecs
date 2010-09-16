# -*- coding: utf-8 -*-

import threading


current_user_store = threading.local()

class GlobalUserMiddleware(object):
    def process_request(self, request):
        if request.user:
            current_user_store.user = request.user
        return None
    
    def process_response(self, request, response):
        if hasattr(current_user_store, 'user'):
            del current_user_store.user
        return response
    
    def process_exception(self, request, exception):
        if hasattr(current_user_store, 'user'):
            del current_user_store.user
        return None

