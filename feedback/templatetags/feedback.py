from django import template

register = template.Library()


# work around for pre Django 1.2

@register.filter
def less(x, y):
    return x < y

@register.filter
def greater(x, y):
    return x > y


# poor man's translation

types_de = {
    'i': ('Ihre', 'Idee', 'Ideen', 'Ihrer Idee'),
    'q': ('Ihre', 'Frage', 'Fragen', 'Ihrer Frage'),
    'p': ('Ihr', 'Problem', 'Probleme', 'Ihres Problems'),
    'l': ('Ihr', 'Lob', 'Lob', 'Ihres Lobs'),
}

types_de_whatever = ('Ihr', 'Irgendwas', 'Irgendwas', 'Ihres Irgendwas')

@register.filter
def fb_type_your(type):
    return types_de.get(type, types_de_whatever)[0]

@register.filter
def fb_type(type):
    return types_de.get(type, types_de_whatever)[1]

@register.filter
def fb_type_many(type):
    return types_de.get(type, types_de_whatever)[2]

@register.filter
def fb_type_of_your(type):
    return types_de.get(type, types_de_whatever)[3]
