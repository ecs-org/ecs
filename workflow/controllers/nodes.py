import imp
import datetime
from django.conf import settings
from django.db import models
from django.utils.importlib import import_module
from django.contrib.contenttypes.models import ContentType

from ecs.utils import cached_property
from ecs.workflow.signals import token_received, deadline_reached
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
        meta = attrs.pop('Meta', None)
        parents = [b for b in bases if isinstance(b, NodeControllerBase)]
        newcls = super(NodeControllerBase, cls).__new__(cls, name, bases, attrs)
        if not parents:
            return newcls
        newcls._meta = NodeControllerOptions(meta, newcls)
        newcls._meta.name = add_controller(newcls)
        return newcls



class NodeController(object):
    __metaclass__ = NodeControllerBase
    
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

    def unlock(self):
        locked = self.is_locked()
        if locked:
            for token in self.get_tokens(locked=False):
                token.lock()
        else:
            for token in self.get_tokens(locked=True):
                token.unlock()
        return locked
    
    def emit_token(self, deadline=False, trail=()):
        tokens = []
        for edge in self.node.edges.filter(deadline=deadline).select_related('to_node'):
            if edge.bind_guard(self.workflow)():
                try:
                    token = edge.to_node.bind(self.workflow).receive_token(self.node, trail=trail)
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
            
    def receive_token(self, source, trail=()):
        if not self.is_reentrant() and self.has_tokens(consumed=None):
            raise TokenRejected("%s is not repeatable" % self.node)
        token = self.workflow.tokens.create(
            node=self.node, 
            source=source, 
            deadline=self.get_deadline(),
            locked=self.is_locked(),
        )
        if trail:
            token.trail = trail
        token_received.send(token)
        return token

    def handle_deadline(self, token):
        deadline_reached.send(token)
        self.progress(token, deadline=True)
        
    def get_deadline(self):
        deadline = self.deadline
        if deadline is None:
            return None
        if isinstance(deadline, datetime.timedelta):
            return datetime.datetime.now() + self.deadline
        elif isinstance(deadline, datetime.datetime):
            return deadline
        else:
            raise TypeError("NodeHandler.deadline must be of type datetime or timedelta or None")
            
    def get_url(self):
        return None
        
    def get_final_urls(self):
        return [self.get_url()]


class Activity(NodeController):
    def perform(self, choice=None):
        self.pre_perform(choice)
        token = self.get_token(locked=False)
        if not token:
            token = self.get_token(locked=True)
            if token:
                raise TokenRequired("Activities cannot be performed with locked tokens")
            elif self.is_repeatable() and self.has_tokens(consumed=None):
                token = self.receive_token(None)
            else:
                raise TokenRequired("Activities cannot be performed without a token")
        self.progress(token)
        self.post_perform(choice, token=token)
        
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
        token = super(FlowController, self).receive_token(source, trail=trail)
        if not self.is_locked():
            self.handle_token(token)

