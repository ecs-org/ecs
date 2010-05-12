import datetime, uuid
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.auth.models import User

from ecs.workflow.controller import registry, NodeHandler
from ecs.workflow.signals import workflow_started, workflow_finished, token_created, token_consumed, token_unlocked, deadline_reached
from ecs.workflow.exceptions import WorkflowError, TokenAlreadyConsumed

NODE_TYPE_CATEGORY_ACTIVITY = 1
NODE_TYPE_CATEGORY_CONTROL = 2
NODE_TYPE_CATEGORY_DYNAMIC_ACTIVITY = 3
NODE_TYPE_CATEGORY_SUBGRAPH = 4

class NodeType(models.Model):
    CATEGORIES = (
        (NODE_TYPE_CATEGORY_ACTIVITY, 'activity'),
        (NODE_TYPE_CATEGORY_CONTROL, 'control'),
        (NODE_TYPE_CATEGORY_DYNAMIC_ACTIVITY, 'dynamic activity'),
        (NODE_TYPE_CATEGORY_SUBGRAPH, 'subgraph'),
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    category = models.PositiveIntegerField(choices=CATEGORIES, db_index=True)
    content_type = models.ForeignKey(ContentType, null=True)
    implementation = models.CharField(max_length=200)
    
    class Meta:
        unique_together = ('content_type', 'implementation')
        
    def save(self, **kwargs):
        if not self.implementation and self.is_subgraph:
            self.implementation = ".%s" % uuid.uuid4().hex
        super(NodeType, self).save(**kwargs)
    
    @property
    def is_subgraph(self):
        return self.category == NODE_TYPE_CATEGORY_SUBGRAPH
        
    @property
    def is_activity(self):
        return self.category == NODE_TYPE_CATEGORY_ACTIVITY
        
    @property
    def is_control(self):
        return self.category == NODE_TYPE_CATEGORY_CONTROL
        
    def __unicode__(self):
        return self.name
        
class GraphManager(models.Manager):
    def create(self, **kwargs):
        model = kwargs.pop('model', None)
        if model:
            kwargs['content_type'] = ContentType.objects.get_for_model(model)
        return super(GraphManager, self).create(**kwargs)

class Graph(NodeType):
    auto_start = models.BooleanField()
    
    objects = GraphManager()
    
    def save(self, **kwargs):
        if not self.category:
            self.category = NODE_TYPE_CATEGORY_SUBGRAPH
        super(Graph, self).save(**kwargs)
    
    @property
    def start_nodes(self):
        return self.nodes.filter(is_start_node=True)

    @property
    def end_nodes(self):
        return self.nodes.filter(is_end_node=True)
        
    def create_node(self, nodetype, start=False, end=False, name=''):
        if isinstance(nodetype, NodeHandler):
            nodetype = nodetype.node_type
        return Node.objects.create(graph=self, node_type=nodetype, is_start_node=start, is_end_node=end, name=name)
        
    def start_workflow(self, **kwargs):
        return Workflow.objects.create(graph=self, **kwargs)


class Guard(models.Model):
    name = models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType)
    implementation = models.CharField(max_length=200)
    
    class Meta:
        unique_together = ('content_type', 'implementation')


class Node(models.Model):
    name = models.CharField(max_length=100, blank=True)
    graph = models.ForeignKey(Graph, related_name='nodes')
    node_type = models.ForeignKey(NodeType)
    outputs = models.ManyToManyField('self', related_name='inputs', through='Edge', symmetrical=False)
    is_start_node = models.BooleanField(default=False)
    is_end_node = models.BooleanField(default=False)

    def __unicode__(self):
        return u"%s (#%s)" % (self.node_type, self.pk)

    def add_edge(self, to, guard=None, negate=False, deadline=False):
        if guard:
            guard = guard.instance
        return Edge.objects.create(from_node=self, to_node=to, guard=guard, negate=negate, deadline=deadline)
        
    def receive_token(self, workflow, source=None, trail=None):
        flow_controller = registry.get_handler(self)
        token = workflow.tokens.create(
            node=self, 
            source=source, 
            deadline=flow_controller.get_deadline(self, workflow),
            locked=flow_controller.is_locked(self, workflow),
        )
        if trail:
            token.trail = trail
        token_created.send(token)
        flow_controller.receive_token(token)
        
    def get_tokens(self, workflow, locked=None):
        tokens = workflow.get_tokens().filter(node=self)
        if locked is not None:
            tokens = tokens.filter(locked=locked)
        return tokens
    
    def get_token(self, workflow, locked=None):
        tokens = self.get_tokens(workflow, locked=locked)[:1]
        if tokens:
            return tokens[0]
        return None
    
    def progress(self, *tokens, **kwargs):
        assert tokens, "Node.progress() must be called with at least one Token instance"
        deadline = kwargs.pop('deadline', False)
        workflow = tokens[0].workflow
        for token in tokens:
            token.consume()
        if self.is_end_node:
            workflow.finish(self)
        else:
            for edge in self.edges.filter(deadline=deadline).select_related('to_node'):
                if edge.check_guard(workflow):
                    edge.to_node.receive_token(workflow, source=self, trail=tokens)
    
    def handle_deadline(self, token):
        registry.get_handler(self).handle_deadline(token)
        deadline_reached.send(token)
        self.progress(token, deadline=True)
        
    def unlock(self, workflow):
        registry.get_handler(self).unlock(self, workflow)


class Edge(models.Model):
    from_node = models.ForeignKey(Node, related_name='edges', null=True)
    to_node = models.ForeignKey(Node, related_name='incoming_edges', null=True)
    deadline = models.BooleanField(default=False)
    guard = models.ForeignKey(Guard, related_name='nodes', null=True)
    negate = models.BooleanField(default=False)
    
    def check_guard(self, workflow):
        if not self.guard_id:
            return True
        return self.negate != registry.get_guard(self).check(workflow)


class Workflow(models.Model):
    content_type = models.ForeignKey(ContentType)
    data_id = models.PositiveIntegerField()
    data = GenericForeignKey(ct_field='content_type', fk_field='data_id')
    graph = models.ForeignKey(Graph, related_name='workflows')
    is_finished = models.BooleanField(default=False)
    parent = models.ForeignKey('workflow.Token', null=True, related_name='parent_workflow')
    
    def clear_tokens(self):
        self.get_tokens().consume()

    def get_tokens(self):
        return self.tokens.filter(consumed_at=None)
        
    def start(self):
        for node in self.graph.start_nodes:
            node.receive_token(self)
        workflow_started.send(self)
        
    def finish(self, node=None):
        self.clear_tokens()
        self.is_finished = True
        self.save(force_update=True)
        workflow_finished.send(self)
        if self.parent:
            self.parent.node.progress(self.parent)
        

class TokenManager(models.Manager):
    def get_query_set(self):
        return TokenQuerySet(self.model)

class TokenQuerySet(models.query.QuerySet):
    def consume(self, **kwargs):
        timestamp = datetime.datetime.now()
        for token in self:
            token.consume(timestamp=timestamp)

    def unlock(self):
        for token in self:
            token.unlock()

class Token(models.Model):
    workflow = models.ForeignKey(Workflow, related_name='tokens')
    node = models.ForeignKey(Node, related_name='tokens')
    trail = models.ManyToManyField('self', related_name='future', symmetrical=False)
    source = models.ForeignKey(Node, related_name='sent_tokens', null=True) # denormalized: can be derived from trail
    deadline = models.DateTimeField(null=True)
    locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    consumed_at = models.DateTimeField(null=True, blank=True, default=None)
    consumed_by = models.ForeignKey(User, null=True, blank=True)
    
    objects = TokenManager()
    
    def consume(self, timestamp=None):
        if self.consumed_at:
            raise TokenAlreadyConsumed()
        self.consumed_at = timestamp or datetime.datetime.now()
        self.save()
        token_consumed.send(self)
        
    def unlock(self):
        if not self.locked:
            return False
        self.locked = False
        self.save()
        token_unlocked.send(self)
        return True

    @property
    def is_consumed(self):
        return self.consumed_at is not None
        
    def handle_deadline(self):
        if not self.deadline:
            return
        self.node.handle_deadline(self)
    
    @property
    def activity_trail(self):
        act_trail = set()
        for token in self.trail.select_related('node__node_type'):
            if token.node.node_type.is_activity:
                act_trail.add(token)
            else:
                act_trail.update(token.activity_trail)
        return act_trail
        
    def __repr__(self):
        return "<Token: workflow=%s, node=%s, consumed=%s>" % (self.workflow, self.node, self.is_consumed)


import sys
if 'test' in sys.argv:
    class Foo(models.Model):
        flag = models.BooleanField(default=False)

        class Meta:
            app_label = 'workflow'
