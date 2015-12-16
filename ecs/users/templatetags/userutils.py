# -*- coding: utf-8 -*-

from django.template import Library, Node

from ecs.users.utils import get_formal_name, get_full_name, sudo


register = Library()

@register.filter
def has_flag(user, flag):
    return not user.is_anonymous() and getattr(user.profile, flag, False)

@register.filter
def is_member_of(user, groupname):
    return user.groups.filter(name=groupname).exists()

@register.filter
def formal_name(user):
    return get_formal_name(user)

@register.filter
def full_name(user):
    return get_full_name(user)

@register.filter
def has_perm(user, permission):
    return bool(user.has_perm(permission))

@register.tag(name='sudo')
def do_sudo(parser, token):
    nodelist = parser.parse(('endsudo',))
    parser.delete_first_token()
    return SudoNode(nodelist)

class SudoNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        with sudo():
            return self.nodelist.render(context)
