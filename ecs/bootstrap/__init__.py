
def register(depends_on=()):
    def decorator(func):
        func.bootstrap = True
        func.depends_on = depends_on
        return func
    return decorator