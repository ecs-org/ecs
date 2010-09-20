from django.db.models import F, Q
from django.conf import settings

_authorization_q_factories = {}

def register(model, factory):
    _authorization_q_factories[model] = factory
    
def make_q_factory(model, prefix=None):
    if prefix:
        for lookup in prefix.split('__'):
            try:
                model = model._meta.get_field(lookup).rel.to
            except AttributeError:
                raise Exception("cannot lookup %s.%s for authoriation" % (model, lookup))
    q_factory = _authorization_q_factories.get(model, None)
    if not q_factory:
        return None
    return q_factory(prefix)
    

class AuthorizationQFactory(object):
    def __init__(self, prefix):
        self.prefix = prefix

    def make_q(self, **lookups):
        if not self.prefix:
            return Q(**lookups)
        return Q(**dict(('%s__%s' % (self.prefix, key), val) for key, val in lookups.iteritems()))
        
    def make_deny_q(self):
        return Q(pk=None)

    def make_f(self, lookup):
        if not self.prefix:
            return F(lookup)
        return F('%s__%s' % (self.prefix, lookup))

    def __call__(self, user):
        if not user or user.is_superuser:
            return Q()
        if user.is_anonymous():
            return self.make_deny_q() # exclude all
        return self.get_q(user)

    def get_q(self, user):
        return Q()

