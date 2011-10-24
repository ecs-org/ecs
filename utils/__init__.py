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
        
    def pop(self, key, *default):
        if isinstance(key, str):
            return self.kwargs.pop(key, *default)
        try:
            x = self.args[key]
            self.args = self.args[:key] + self.args[key + 1:]
            return x
        except IndexError:
            if default:
                return default[0]
            raise
    
    def get(self, key, default=None):
        if isinstance(key, str):
            try:
                return self.kwargs[key]
            except KeyError:
                return default
        else:
            try:
                return self.args[key]
            except IndexError:
                return default
    
    def __getitem__(self, key):
        if isinstance(key, str):
            return self.kwargs[key]
        return self.args[key]
        
    def __nonzero__(self):
        return bool(self.args or self.kwargs)
