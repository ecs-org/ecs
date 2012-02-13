# -*- coding: utf-8 -*-
from django import template

from ecs.help.utils import parse_index, ParseError

register = template.Library()

@register.filter
def prevtopnext(page):
    def _find(tree, top=None):
        for i, el in enumerate(tree):
            result = {'top': top, 'prev': None, 'next': None}
            try:
                result['prev'] = [e for e in tree[:i] if not isinstance(e, list)][-1]
            except IndexError:
                pass
            try:
                result['next'] = [e for e in tree[i+1:] if not isinstance(e, list)][0]
            except IndexError:
                pass
            if isinstance(el, list):
                ret = _find(el, top=result['prev'])
                if ret:
                    return ret
            elif el == page:
                return result
        return None
    try:
        return _find(parse_index())
    except ParseError:
        return None
