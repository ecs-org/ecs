import datetime
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.functional import wraps
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
        token = node.peek_token(workflow, locked=False)
        if not token:
            if node.peek_token(workflow, locked=True):
                raise TokenRequired("Activities cannot be performed with locked tokens")
            raise TokenRequired("Activities cannot be performed without a token")
        token.consume()
        try:
            return self(token)
        finally:
            node.progress(workflow)
        
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

_activities = {}
_guards = {}
_controls = {}
_node_type_map = {}
_guard_map = {}

def clear_caches():
    for handler in _node_type_map.itervalues():
        del handler.node_type
    for g in _guard_map.itervalues():
        del g.instance


def get_handler(node):
    try:
        return _node_type_map[node.node_type_id]
    except KeyError:
        if node.node_type.is_subgraph:
            return _controls['ecs.workflow.patterns.subgraph']
        raise KeyError("Missing FlowHandler for NodeType %s" % node.node_type)


def get_guard(edge):
    try:
        return _guard_map[edge.guard_id]
    except KeyError:
        raise KeyError("Unknown guard: %s" % edge.guard)


def control(factory=Control, **kwargs):
    def decorator(func):
        control = factory(func, **kwargs)
        _controls[control.name] = control
        return wraps(func)(control)
    return decorator


def activity(model=None, factory=Activity, **kwargs):
    def decorator(func):
        act = factory(func, model=model, **kwargs)
        model_activities = _activities.setdefault(model, {})
        model_activities[act.name] = act
        return wraps(func)(act)
    return decorator


def guard(model=None, factory=Guard, **kwargs):
    def decorator(func):
        guard = factory(func, model=model, **kwargs)
        _guards.setdefault(model, {})[guard.name] = guard
        return wraps(func)(guard)
    return decorator
