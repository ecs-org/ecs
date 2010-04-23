# encoding: utf-8

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


# work around for pre Django 1.2

@register.filter
def less(x, y):
    return x < y

@register.filter
def greater(x, y):
    return x > y


# intergalactic translator

types_de = {
    'i': (u'Ihre', u'Idee', u'Ideen', u'Ihrer Idee', u'Keine'),
    'q': (u'Ihre', u'Frage', u'Fragen', u'Ihrer Frage', u'Keine'),
    'p': (u'Ihr', u'Problem', u'Probleme', u'Ihres Problems', u'Keine'),
    'l': (u'Ihr', u'Lob', u'Lob', u'Ihres Lobs', u'Kein')
}

types_de_whatever = (u'Ihr', u'Irgendwas', u'Irgendwas', u'Ihres Irgendwas', u'Kein')

@register.filter
@stringfilter
def fb_type_your(type):
    return types_de.get(type, types_de_whatever)[0]

@register.filter
@stringfilter
def fb_type(type):
    return types_de.get(type, types_de_whatever)[1]

@register.filter
@stringfilter
def fb_type_many(type):
    return types_de.get(type, types_de_whatever)[2]

@register.filter
@stringfilter
def fb_type_of_your(type):
    return types_de.get(type, types_de_whatever)[3]

@register.filter
@stringfilter
def fb_type_none(type):
    return types_de.get(type, types_de_whatever)[4]


@register.filter
def fb_type_items(type, items):
    if items == 1:
        return fb_type(type)
    else:
        return fb_type_many(type)


motivation_de = {
    'i': u'Teilen Sie Ihre Idee mit',
    'q': u'Stellen Sie Ihre Frage',
    'p': u'Beschreiben Sie Ihr Problem',
    'l': u'Geben Sie Lob'
}

@register.filter
@stringfilter
def fb_motivate(type):
    return motivation_de.get(type, u'Uh oh, da geht gerade etwas schief ..')


others_de = {
    (0, 'yours', 'i'): u'Niemanden sonst gefällt Ihre Idee',
    (0, 'u2',    'i'): u'(das sollte nun wirklich gar nicht vorkommen)',
    (0, 'me2',   'i'): u'Niemanden gefällt diese Idee',
    (1, 'yours', 'i'): u'Einer weiteren Person gefällt Ihre Idee',
    (1, 'u2',    'i'): u'Ihnen gefällt diese Idee',
    (1, 'me2',   'i'): u'Einer Person gefällt diese Idee',
    (2, 'yours', 'i'): u'%s weiteren Personen gefällt Ihre Idee',
    (2, 'u2',    'i'): u'%s Personen gefällt diese Idee',
    (2, 'me2',   'i'): u'%s Personen gefällt diese Idee',

    (0, 'yours', 'q'): u'Niemand sonst hat ebenfalls Ihre Frage',
    (0, 'u2',    'q'): u'(wenn das der Admin sieht)',
    (0, 'me2',   'q'): u'Niemand hat ebenfalls diese Frage',
    (1, 'yours', 'q'): u'Eine weitere Person hat ebenfalls Ihre Frage',
    (1, 'u2',    'q'): u'Sie haben ebenfalls diese Frage',
    (1, 'me2',   'q'): u'Eine Person hat ebenfalls diese Frage',
    (2, 'yours', 'q'): u'%s weitere Personen haben ebenfalls Ihre Frage',
    (2, 'u2',    'q'): u'%s Personen haben ebenfalls diese Frage',
    (2, 'me2',   'q'): u'%s Personen haben ebenfalls diese Frage',

    (0, 'yours', 'p'): u'Niemand sonst hat ebenfalls Ihr Problem',
    (0, 'u2',    'p'): u'(jodeldü)',
    (0, 'me2',   'p'): u'Niemand hat ebenfalls dieses Problem',
    (1, 'yours', 'p'): u'Eine weitere Person hat ebenfalls Ihr Problem',
    (1, 'u2',    'p'): u'Sie haben ebenfalls dieses Problem',
    (1, 'me2',   'p'): u'Eine Person hat ebenfalls dieses Problem',
    (2, 'yours', 'p'): u'%s weitere Personen haben ebenfalls Ihr Problem',
    (2, 'u2',    'p'): u'%s Personen haben ebenfalls dieses Problem',
    (2, 'me2',   'p'): u'%s Personen haben ebenfalls dieses Problem',

    (0, 'yours', 'l'): u'Niemand sonst möchte Ihr Lob aussprechen',
    (0, 'u2',    'l'): u'(meine CPU ist heissgelaufen)',
    (0, 'me2',   'l'): u'Niemand möchte ebenfalls dieses Lob aussprechen',
    (1, 'yours', 'l'): u'Eine weitere Person möchte ebenfalls Ihr Lob aussprechen',
    (1, 'u2',    'l'): u'Sie haben ebenfalls dieses Lob ausgesprochen',
    (1, 'me2',   'l'): u'Eine Person möchte ebenfalls dieses Lob aussprechen',
    (2, 'yours', 'l'): u'%s weitere Personen möchten ebenfalls Ihr Lob aussprechen',
    (2, 'u2',    'l'): u'%s Personen haben ebenfalls dieses Lob ausgesprochen',
    (2, 'me2',   'l'): u'%s Personen haben ebenfalls dieses Lob ausgesprochen'
}

@register.filter
def fb_count(type, count):
    return (type, count)

@register.filter
def fb_me2(pair, me2):
    type = pair[0]
    count = pair[1]
    if count < 2:
        s = others_de.get((count, me2, type), u'Tja .. (%s, %s, %s)' % (count, me2, type))
        return s
    else:
        s = others_de.get((2, me2, type), u'Tsk, tsk .. (%s, %s, %s)' % (count, me2, type))
        return s % count


# truncate string after max characters

@register.filter
def truncate(s, max):
    n = len(s)
    if n > max:
        dots = u' ..'
        return s[0:max-len(dots)] + dots
    else:
        return s


# translate Python booleans to JavaScript

@register.filter
def booljs(x):
    return x and 'true' or 'false'


# decode feedback origin strings

@register.filter
@stringfilter
def fb_origin(origin):
    import re, urllib
    return urllib.unquote(re.sub(r'-([0-9A-F]{2})', lambda mo: '%' + mo.group(0)[1:3], origin).replace('--', '-'))



