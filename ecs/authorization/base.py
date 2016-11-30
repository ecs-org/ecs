from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

class QFactoryRegistry(object):
    def __init__(self):
        self.q_factories = {}
        self.lookups = {}
        self.loaded = False
        
    def register(self, model, factory=None, lookup=None):
        if not factory and not lookup:
            raise TypeError("register requires a `factory` or a `lookup` argument")
        if factory:
            self.q_factories[model] = factory
        if lookup:
            self.lookups[model] = lookup

    def load_authorization_config(self):
        if self.loaded:
            return
        __import__(settings.AUTHORIZATION_CONFIG)
        self.loaded = True
    
    def get_q_factory(self, model):
        self.load_authorization_config()
        target_model = model
        lookup = self.lookups.get(model)
        if lookup:
            for bit in lookup.split('__'):
                try:
                    target_model = target_model._meta.get_field(bit).rel.to
                except AttributeError:
                    raise Exception("cannot lookup %s.%s for authoriation" % (target_model, bit))
        q_factory = self.q_factories.get(target_model, None)
        if not q_factory:
            raise ImproperlyConfigured("The model %s uses an AuthorizationManager with lookup '%s' which resolves to %s, but no matching QFactory was provided." % (
                model.__name__, self._lookup, target_model.__name__,
            ))
        return q_factory(lookup, target_model)
        

class QFactory(object):
    def __init__(self, lookup, model):
        self.lookup = lookup
        self.model = model

    def make_q(self, **lookups):
        return Q(**lookups)

    def make_deny_q(self):
        return Q(pk=None)

    def __call__(self, user):
        if not user or user.is_superuser:
            return Q()
        elif user.is_anonymous():
            return self.make_deny_q() # exclude all
        if not self.lookup:
            return self.get_q(user)
        return Q(**{'%s__pk__in' % (self.lookup,): self.model.objects.all().values('pk').query})

    def get_q(self, user):
        return Q()


registry = QFactoryRegistry()
register = registry.register
get_q_factory = registry.get_q_factory
