import re

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
        
        
_camel_split_re = re.compile(r'[A-Z0-9]+(?![a-z])|\w[^A-Z]+')
def camel_split(s):
    return [m.group(0) for m in _camel_split_re.finditer(s)]


class Args(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        
    def update(self, *args, **kwargs):
        self.args += args
        self.kwargs.update(kwargs)
        
    def apply(self, func):
        return func(*self.args, **self.kwargs)
        
    def setdefault(self, key, value):
        self.kwargs.setdefault(key, value)
        
    def __getitem__(self, key):
        if isinstance(key, str):
            return self.kwargs[key]
        return self.args[key]
        
    def __nonzero__(self):
        return bool(self.args or self.kwargs)
    