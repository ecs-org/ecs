from django.template import Library

register = Library()

register.filter('getattr', lambda obj, name: getattr(obj, str(name)))
register.filter('getitem', lambda obj, name: obj[name])
