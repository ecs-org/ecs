from django import template

register = template.Library()


# work around for pre Django 1.2

@register.filter
def less(x, y):
    return x < y

@register.filter
def greater(x, y):
    return x > y


# poor man's translator

types_de = {
    'i': ('Ihre', 'Idee', 'Ideen', 'Ihrer Idee', 'diese Idee'),
    'q': ('Ihre', 'Frage', 'Fragen', 'Ihrer Frage', 'diese Frage'),
    'p': ('Ihr', 'Problem', 'Probleme', 'Ihres Problems', 'dieses Problem'),
    'l': ('Ihr', 'Lob', 'Lob', 'Ihres Lobs', 'dieses Lob'),
}

types_de_whatever = ('Ihr', 'Irgendwas', 'Irgendwas', 'Ihres Irgendwas', 'dieses Irgendwas')

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

@register.filter
def fb_type_this(type):
    return types_de.get(type, types_de_whatever)[4]

@register.filter
def fb_type_items(type, items):
    if items == 1:
        return fb_type(type)
    else:
        return fb_type_many(type)


person_de = ('Niemanden', 'Einer Person', 'Personen')

@register.filter
def fb_count_persons(count):
    if count == 0:
        return person_de[0]
    elif count == 1:
        return person_de[1]
    else:
        return '%s %s' % (count, person_de[2])


