from django.utils.functional import wraps

def tracking_hint(exclude=False, **kwargs):
    def decorator(view):
        @wraps(view)
        def decorated(request, *args, **kwargs):
            if exclude:
                request.tracking_data = None
            return view(request, *args, **kwargs)
        if kwargs:
            decorated.tracking_hints = kwargs
        return decorated
    return decorator
    
