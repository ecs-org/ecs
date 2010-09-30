
class CachedProperty(object):
    def __init__(self, func, attr=None):
        self.func = func
        self.attr = attr or "_%s_cache" % func.__name__
        
    def __get__(self, instance, instance_type=None):
        if not hasattr(instance, self.attr):
            setattr(instance, self.attr, self.func(instance))
        return getattr(instance, self.attr)
        
    def __set__(self, instance, value):
        setattr(instance, self.attr, value)
        
    def __delete__(self, instance):
        if hasattr(instance, self.attr):
            delattr(instance, self.attr)
        
def cached_property(arg):
    if isinstance(arg, str):
        def decorator(func):
            return CachedProperty(func, arg)
        return decorator
    else:
        return CachedProperty(arg)

class Args(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        
    def update(self, *args, **kwargs):
        self.args += args
        self.kwargs.update(kwargs)
        
    def apply(self, func):
        return func(*self.args, **self.kwargs)
        
    def __nonzero__(self):
        return bool(self.args and self.kwargs)
    