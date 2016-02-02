from django.template import Library
from django.contrib import messages


register = Library()


@register.filter
def level2alert(lvl):
    '''
    Translate django.contrib.auth message levels to bootstrap alert classes.
    '''
    tr = {
        messages.SUCCESS: 'success',
        messages.WARNING: 'warning',
        messages.ERROR: 'danger',
    }
    return tr.get(lvl, 'info')
