import datetime, imp

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.functional import wraps
from django.utils.importlib import import_module
from django.conf import settings

from ecs.utils import cached_property
from ecs.workflow.exceptions import TokenRequired


class NodeHandler(object):
    def __init__(self, func, model=None, deadline=None, lock=None, signal=None):
        self.name = "%s.%s" % (func.__module__, func.__name__)
        self.model = model
        self.func = func
        self.deadline = deadline
        self.lock = lock
        if signal:
            signal.connect(self._signal_listener)
            
    def _signal_listener(self, sender, **kwargs):
        if isinstance(sender, models.base.ModelBase):
            sender = kwargs['instance']
        sender.workflow.unlock(self)
        
    @cached_property
    def node_type(self):
        from ecs.workflow.models import NodeType
        if self.model:
            ct = ContentType.objects.get_for_model(self.model)
        else:
            ct = None
        try:
            return NodeType.objects.get(implementation=self.name, content_type=ct)
        except NodeType.DoesNotExist:
            raise RuntimeError("%s is not synced to the database. Forgot to run the workflow_sync command?" % self)
        
    def is_locked(self, node, workflow):
        if not self.lock:
            return False
        return not self.lock(workflow)

    def get_deadline(self, node, workflow):
        if self.deadline is None:
            return None
        if callable(self.deadline):
            return self.deadline(node, workflow)
        return datetime.datetime.now() + self.deadline
        
    def unlock(self, node, workflow):
        if not self.is_locked(node, workflow):
            node.get_tokens(workflow, locked=True).unlock()

    def receive_token(self, token):
        pass

    def handle_deadline(self, token):
        pass
        
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class Activity(NodeHandler):
    def __init__(self, func, auto=False, **kwargs):
        super(Activity, self).__init__(func, **kwargs)
        self.auto = auto
        
    def _signal_listener(self, sender, **kwargs):
        super(Activity, self)._signal_listener(sender, **kwargs)
        if self.auto:
            sender.workflow.do(self)
            
    def perform(self, node, workflow):
        token = node.get_token(workflow, locked=False)
        if not token:
            if node.get_token(workflow, locked=True):
                raise TokenRequired("Activities cannot be performed with locked tokens")
            raise TokenRequired("Activities cannot be performed without a token")
        try:
            return self(token)
        finally:
            node.progress(token)
        
    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.name)
        

class Control(NodeHandler):
    def _signal_listener(self, sender, **kwargs):
        super(Control, self)._signal_listener(sender, **kwargs)
        
    def receive_token(self, token):
        if not self.is_locked(token.node, token.workflow):
            self(token)


class Guard(object):
    def __init__(self, func, name=None, model=None):
        self.model = model
        self.name = name or func.__name__
        self.func = func
        
    @cached_property
    def instance(self):
        from ecs.workflow.models import Guard
        if self.model:
            ct = ContentType.objects.get_for_model(self.model)
        else:
            ct = None
        try:
            return Guard.objects.get(content_type=ct, implementation=self.name)
        except Guard.DoesNotExist:
            raise RuntimeError("Guard %s is not synced to the database. Forgot to run the workflow_sync command?" % self)
    
    def __call__(self, workflow):
        return self.func(workflow)
        
    def check(self, workflow):
        return self(workflow)


class Registry(object):
    def __init__(self):
        self._activities = {}
        self._guards = {}
        self._controls = {}
        self._node_type_map = {}
        self._guard_map = {}
        self.loaded = False

    def clear_caches(self):
        for handler in self._node_type_map.itervalues():
            del handler.node_type
        for g in self._guard_map.itervalues():
            del g.instance
            
    def autodiscover(self):
        for app in settings.INSTALLED_APPS:
            try:
                app_path = import_module(app).__path__
            except AttributeError:
                continue
            try:
                imp.find_module('workflow', app_path)
            except ImportError:
                continue
            module = import_module("%s.workflow" % app)
            
    def _load(self):
        if self.loaded:
            return
        import ecs.workflow.patterns
        self.autodiscover()
        self.loaded = True

    def get_handler(self, node):
        self._load()
        try:
            return self._node_type_map[node.node_type_id]
        except KeyError:
            if node.node_type.is_subgraph:
                return self._controls['ecs.workflow.patterns.subgraph']
            raise KeyError("Missing FlowHandler for NodeType %s" % node.node_type)

    def get_guard(self, edge):
        self._load()
        try:
            return self._guard_map[edge.guard_id]
        except KeyError:
            raise KeyError("Unknown guard: %s" % edge.guard)
            
    @property
    def activities(self):
        self._load()
        return self._activities.itervalues()
        
    @property
    def controls(self):
        self._load()
        return self._controls.itervalues()
        
    @property
    def guards(self):
        self._load()
        return self._guards.itervalues()

    ## DECORATORS: ##

    def control(self, factory=Control, **kwargs):
        def decorator(func):
            control = factory(func, **kwargs)
            self._controls[control.name] = control
            return wraps(func)(control)
        return decorator

    def activity(self, model=None, factory=Activity, **kwargs):
        def decorator(func):
            act = factory(func, model=model, **kwargs)
            self._activities[act.name] = act
            return wraps(func)(act)
        return decorator

    def guard(self, model=None, factory=Guard, **kwargs):
        def decorator(func):
            guard = factory(func, model=model, **kwargs)
            self._guards[guard.name] = guard
            return wraps(func)(guard)
        return decorator

registry = Registry()
