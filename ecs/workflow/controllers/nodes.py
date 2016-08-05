import datetime

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from ecs.utils import cached_property
from ecs.workflow.signals import token_received
from ecs.workflow.exceptions import TokenRequired, TokenRejected
from ecs.workflow.controllers.registry import add_controller

class NodeControllerOptions(object):
    def __init__(self, meta, cls):
        self.cls = cls
        self.model = getattr(meta, 'model', None)
        self.vary_on = getattr(meta, 'vary_on', None)
        self.auto = getattr(meta, 'auto', False)
        update_lock = getattr(meta, 'update_lock', None)
        # XXX: update_deadline = getattr(meta, 'update_deadline', None)
        if update_lock:
            lock_signal, lock_kwarg = update_lock
            def _unlock(sender, **kwargs):
                kwargs[unlock_kwarg].workflow.unlock()
            unlock_signal.connect(_unlock, sender=self.model)

    def copy(self, meta, cls):
        new = NodeControllerOptions(None, cls)
        for k in ('model', 'vary_on', 'auto', 'update_lock'):
            setattr(new, k, getattr(meta, k, None) or getattr(self, k, None))
        return new

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
            raise RuntimeError("%s is not synced to the database. Forgot to run the workflow_sync command?" % self.cls)

class NodeControllerBase(type):
    def __new__(cls, name, bases, attrs):
        attr_meta = attrs.pop('Meta', None)
        newcls = super().__new__(cls, name, bases, attrs)
        parents = [b for b in bases if isinstance(b, NodeControllerBase)]
        if not parents:
            return newcls
        old_meta = getattr(newcls, '_meta', None)
        newcls._meta = old_meta.copy(attr_meta, newcls) if old_meta else NodeControllerOptions(attr_meta, newcls)
        newcls._meta.name = add_controller(newcls)
        return newcls

class NodeController(object, metaclass=NodeControllerBase):
    deadline = None
    
    def __init__(self, node, workflow):
        self.node = node
        self.workflow = workflow
        
    def get_tokens(self, locked=None, consumed=False):
        tokens = self.workflow.tokens.filter(node=self.node)
        if consumed is not None:
            tokens = tokens.filter(consumed_at__isnull=not consumed)
        if locked is not None:
            tokens = tokens.filter(locked=locked)
        return tokens

    def get_token(self, locked=None, consumed=False):
        tokens = self.get_tokens(locked=locked, consumed=consumed)[:1]
        if tokens:
            return tokens[0]
        return None
        
    def has_tokens(self, locked=None, consumed=False):
        return self.get_tokens(locked=locked, consumed=consumed).exists()

    def is_locked(self):
        return False

    def is_reentrant(self):
        return True
        
    def unlock_token(self, token):
        return token.unlock()
        
    def lock_token(self, token):
        return token.lock()

    def unlock(self):
        locked = self.is_locked()
        if locked:
            for token in self.get_tokens(locked=False):
                self.lock_token(token)
        else:
            for token in self.get_tokens(locked=True):
                self.unlock_token(token)
        return locked
    
    def emit_token(self, deadline=False, trail=()):
        tokens = []
        for edge in self.node.edges.filter(deadline=deadline).select_related('to_node'):
            if edge.bind_guard(self.workflow)():
                try:
                    token = edge.to_node.bind(self.workflow).receive_token(self.node, trail=trail)
                    if token:
                        tokens.append(token)
                except TokenRejected:
                    pass
        return tokens
    
    def progress(self, *tokens, **kwargs):
        assert tokens, "NodeController.progress() must be called with at least one Token instance"
        deadline = kwargs.pop('deadline', False)
        for token in tokens:
            assert token.node == self.node, "NodeControllers should only consume tokens on their own node."
            token.consume()
        if self.node.is_end_node:
            self.workflow.finish(self.node)
        else:
            self.emit_token(deadline=deadline, trail=tokens)
            
    def receive_token(self, source, trail=(), repeated=False):
        reentrant = self.is_reentrant()
        if not reentrant and self.has_tokens(consumed=None):
            raise TokenRejected("%s is not repeatable" % self.node)
        token = self.workflow.tokens.create(
            node=self.node, 
            source=source, 
            deadline=self.get_deadline(),
            locked=self.is_locked(),
            repeated=repeated,
        )
        if trail:
            token.trail = trail
        token_received.send(token)
        return token
        
    def get_deadline(self):
        deadline = self.deadline
        if deadline is None:
            return None
        if isinstance(deadline, datetime.timedelta):
            return timezone.now() + self.deadline
        elif isinstance(deadline, datetime.datetime):
            return deadline
        else:
            raise TypeError("NodeHandler.deadline must be of type datetime or timedelta or None")
            
    def get_url(self):
        return None
        
    def get_final_urls(self):
        return [self.get_url()]

    def get_afterlife_url(self):
        return None


class Activity(NodeController):
    def perform(self, choice=None, token=None):
        self.pre_perform(choice)
        if token is None:
            token = self.activate()
        self.progress(token)
        self.post_perform(choice, token=token)
        
    def activate(self, reopen=False):
        if reopen and self.is_repeatable() and self.has_tokens(consumed=None):
            return self.receive_token(None, repeated=True)
        token = self.get_token(locked=False)
        if not token:
            if self.is_repeatable() and self.has_tokens(consumed=None):
                token = self.receive_token(None, repeated=True)
            elif self.get_token(locked=True):
                raise TokenRequired("Activities cannot be activated with locked tokens")
            else:
                raise TokenRequired("Activities cannot be activated without a token")
        return token
        
    def is_repeatable(self):
        return False
        
    def get_choices(self):
        return ()
        
    def pre_perform(self, option):
        pass
        
    def post_perform(self, option, token=None):
        pass
        
    def __repr__(self):
        return "<Activity:%s>" % (self.__class__)


class FlowController(NodeController):
    def receive_token(self, source, trail=None):
        token = super().receive_token(source, trail=trail)
        if token and not self.is_locked():
            self.handle_token(token)

    def unlock_token(self, token):
        if super().unlock_token(token):
            self.handle_token(token)
    
