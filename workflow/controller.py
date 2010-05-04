import datetime
from django.db import models
from ecs.workflow.exceptions import TokenRequired

class NodeHandler(object):
    def __init__(self, name, deadline=None, lock=None, signal=None):
        self.name = name
        self.node_type = None
        self.deadline = deadline
        self.lock = lock
        if signal:
            signal.connect(self._signal_listener)
        
    def _signal_listener(self, sender, **kwargs):
        if isinstance(sender, models.base.ModelBase):
            sender = kwargs['instance']
        sender.workflow.unlock(self)
        
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
        
class Activity(NodeHandler):
    def __init__(self, model, name, auto=False, **kwargs):
        super(Activity, self).__init__(name, **kwargs)
        self.model = model
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
        node.progress(workflow)
        
    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.name)
        
class Control(NodeHandler):
    def __init__(self, name, func, **kwargs):
        super(Control, self).__init__(name, **kwargs)
        self.name = name
        self.func = func
        
    def _signal_listener(self, sender, **kwargs):
        super(Control, self)._signal_listener(sender, **kwargs)

    def __call__(self, node, workflow, token=None):
        if not self.is_locked(node, workflow):
            self.func(node, workflow, token)
    
    def receive_token(self, token):
        self(token.node, token.workflow, token)

class Guard(object):
    def __init__(self, model, name, func):
        self.model = model
        self.name = name
        self.func = func
    
    def __call__(self, workflow):
        return self.func(workflow)
        
    def check(self, workflow):
        return self(workflow)

_activities = {}
_guards = {}
_controls = {}
_node_type_map = {}
_guard_map = {}

def declare_activity(model, name, **kwargs):
    # FIXME: handle name conflicts
    activity = Activity(model, name, **kwargs)
    model_activities = _activities.setdefault(model, {})
    model_activities[name] = activity
    return activity
    
def declare_guard(model, name, func, **kwargs):
    # FIXME: handle name conflicts
    guard = Guard(model, name, func, **kwargs)
    _guards.setdefault(model, {})[name] = guard
    return guard
    
def declare_control(name, func):
    # FIXME: handle name conflicts
    control = Control(name, func)
    _controls[name] = control
    return control
    
def get_handler(node):
    try:
        return _node_type_map[node.node_type_id]
    except KeyError:
        if node.node_type.is_subgraph:
            return _controls['subgraph']
        raise KeyError("Missing FlowHandler for NodeType %s" % node.node_type)
        
def get_guard(transition):
    try:
        return _guard_map[transition.guard_id]
    except KeyError:
        raise KeyError("Unknown guard: %s" % transition.guard)
    
def control(func):
    return declare_control(func.__name__, func)
    
# the following flow handlers are based on control pattern descriptions from http://www.workflowpatterns.com/patterns/control/

# Builtin:
# def parallel_split(node, workflow):
# def multi_choice(node, workflow):
# def simple_merge(node, workflow):

@control
def generic(node, workflow, token=None):
    node.pop_token(workflow)
    node.progress(workflow)
    
@control
def subgraph(node, workflow, token=None):
    subworkflow = node.node_type.graph.start_workflow(data=workflow.data, parent=token)
    subworkflow.start()

@control
def synchronization(node, workflow, token=None):
    tokens = node.get_tokens(workflow).select_related('source')
    expected_inputs = set(node.inputs.all())
    synchronized_tokens = set()
    if len(tokens) >= len(expected_inputs):
        for t in tokens:
            if t.source in expected_inputs:
                expected_inputs.remove(t.source)
                synchronized_tokens.add(t)
        if not expected_inputs:
            for t in synchronized_tokens:
                t.consume()
            node.progress(workflow)

# FIXME: we need a cancelling discriminator
@control
def cancelling_discriminator(node, workflow):
    pass

# nice to have
@control
def thread_split(node, workflow):
    pass

@control
def thread_join(node, workflow):
    pass