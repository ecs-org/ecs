from django.utils.functional import wraps

def tracking_hint(exclude=False):
    def decorator(view):
        @wraps(view)
        def decorated(request, *args, **kwargs):
            request.tracking_data = None
            return view(request, *args, **kwargs)
        return decorated
    return decorator
    
