import datetime
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.auth.models import User

from ecs.workflow import controller
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
    implementation = models.CharField(max_length=100)
    
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

class Graph(NodeType):
    auto_start = models.BooleanField()
    
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
        
    def create_node(self, nodetype, start=False, end=False):
        if isinstance(nodetype, controller.NodeHandler):
            nodetype = nodetype.node_type
        return Node.objects.create(graph=self, node_type=nodetype, is_start_node=start, is_end_node=end)
        
    def start_workflow(self, **kwargs):
        return Workflow.objects.create(graph=self, **kwargs)
        
    @property
    def dot(self):
        statements = ['N_Start [shape=point, label=Start]', 'N_End [shape=point, label=End]']
        for node in self.nodes.all():
            shape = 'diamond'
            if node.node_type.category == NODE_TYPE_CATEGORY_ACTIVITY:
                shape = 'box'
            statements.append("N_%s [label=%s, shape=%s, style=rounded]" % (node.pk, node.node_type.name, shape))
            if node.is_end_node:
                statements.append('N_%s -> N_End' % node.pk)
            if node.is_start_node:
                statements.append('N_Start -> N_%s' % node.pk)
        for node in self.nodes.all():
            for edge in node.edges.all():
                if edge.guard_id:
                    label = ' [label=%s%s]' % (edge.negate and '~' or '', edge.guard_id)
                else:
                    label = ''
                statements.append("N_%s -> N_%s%s" % (edge.from_node_id, edge.to_node_id, label))
        return "graph{\n\t%s;\n}" % ";\n\t".join(statements)


class Guard(models.Model):
    content_type = models.ForeignKey(ContentType)
    implementation = models.CharField(max_length=200)


class Node(models.Model):
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
        
    def receive_token(self, workflow, source=None):
        flow_controller = controller.get_handler(self)
        token = workflow.tokens.create(
            node=self, 
            source=source, 
            deadline=flow_controller.get_deadline(self, workflow),
            locked=flow_controller.is_locked(self, workflow),
        )
        token_created.send(token)
        flow_controller.receive_token(token)
        
    def get_tokens(self, workflow, locked=None):
        tokens = workflow.get_tokens().filter(node=self)
        if locked is not None:
            tokens = tokens.filter(locked=locked)
        return tokens
    
    def peek_token(self, workflow, locked=None):
        tokens = self.get_tokens(workflow, locked=locked)[:1]
        if tokens:
            return tokens[0]
        return None
    
    def pop_token(self, workflow, locked=None):
        token = self.peek_token(workflow, locked=locked)
        if token:
            token.consume()
            return token
        return None
        
    def progress(self, workflow, deadline=False):
        if self.is_end_node:
            workflow.finish(self)
        else:
            for edge in self.edges.filter(deadline=deadline).select_related('to_node'):
                if edge.check_guard(workflow):
                    edge.to_node.receive_token(workflow, source=self)
    
    def handle_deadline(self, token):
        controller.get_handler(self).handle_deadline(token)
        deadline_reached.send(token)
        self.progress(token.workflow, deadline=True)
        
    def unlock(self, workflow):
        controller.get_handler(self).unlock(self, workflow)


class Edge(models.Model):
    from_node = models.ForeignKey(Node, related_name='edges', null=True)
    to_node = models.ForeignKey(Node, related_name='incoming_edges', null=True)
    deadline = models.BooleanField(default=False)
    guard = models.ForeignKey(Guard, related_name='nodes', null=True)
    negate = models.BooleanField(default=False)
    
    def check_guard(self, workflow):
        if not self.guard_id:
            return True
        return self.negate != controller.get_guard(self).check(workflow)


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
            self.parent.consume()
            self.parent.node.progress(self.parent.workflow)
        

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
    source = models.ForeignKey(Node, related_name='sent_tokens', null=True)
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
        self.consume()
        self.node.handle_deadline(self)
        
    def __repr__(self):
        return "<Token: workflow=%s, node=%s, consumed=%s>" % (self.workflow, self.node, self.is_consumed)

import sys
if 'test' in sys.argv:
    class Foo(models.Model):
        flag = models.BooleanField(default=False)

        class Meta:
            app_label = 'workflow'
