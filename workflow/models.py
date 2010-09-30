import datetime
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.auth.models import User

from ecs.workflow.controllers import bind_node, bind_edge, bind_guard, NodeController
from ecs.workflow.signals import workflow_started, workflow_finished, token_consumed, token_unlocked, deadline_reached
from ecs.workflow.exceptions import WorkflowError, TokenAlreadyConsumed

NODE_TYPE_CATEGORY_ACTIVITY = 1
NODE_TYPE_CATEGORY_CONTROL = 2
NODE_TYPE_CATEGORY_SUBGRAPH = 3

class NodeTypeManager(models.Manager):
    def create(self, **kwargs):
        model = kwargs.pop('model', None)
        if model:
            kwargs['content_type'] = ContentType.objects.get_for_model(model)
        data_type = kwargs.get('data_type', None)
        if isinstance(data_type, models.base.ModelBase):
            kwargs['data_type'] = ContentType.objects.get_for_model(data_type)
        return super(NodeTypeManager, self).create(**kwargs)

class NodeType(models.Model):
    CATEGORIES = (
        (NODE_TYPE_CATEGORY_ACTIVITY, 'activity'),
        (NODE_TYPE_CATEGORY_CONTROL, 'control'),
        (NODE_TYPE_CATEGORY_SUBGRAPH, 'subgraph'),
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    category = models.PositiveIntegerField(choices=CATEGORIES, db_index=True)
    content_type = models.ForeignKey(ContentType, null=True, related_name='workflow_node_types')
    implementation = models.CharField(max_length=200)
    data_type = models.ForeignKey(ContentType, null=True)
    
    objects = NodeTypeManager()
    
    def save(self, **kwargs):
        if not self.implementation and self.is_subgraph:
            self.implementation = 'ecs.workflow.patterns.Subgraph'
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
        if self.data_type:
            return "%s(%s)" % (self.name, self.data_type)
        return "'%s':%s" % (self.name, self.implementation)
        
class GraphManager(models.Manager):
    def create(self, **kwargs):
        model = kwargs.pop('model', None)
        if model:
            kwargs['content_type'] = ContentType.objects.get_for_model(model)
        return super(GraphManager, self).create(**kwargs)
    
    def _prep_get_kwargs(self, kwargs):
        model = kwargs.pop('model', None)
        if model:
            kwargs['content_type'] = ContentType.objects.get_for_model(model)
        return kwargs
    
    def get(self, **kwargs):
        return super(GraphManager, self).get(**self._prep_get_kwargs(kwargs))
        
    def create(self, **kwargs):
        return super(GraphManager, self).create(**self._prep_get_kwargs(kwargs))

    def get_or_create(self, **kwargs):
        return super(GraphManager, self).get_or_create(**self._prep_get_kwargs(kwargs))


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
        
    def _prep_nodetype(self, nodetype, data=None):
        if isinstance(nodetype, type) and issubclass(nodetype, NodeController):
            nodetype = nodetype._meta.node_type
        if nodetype.data_type:
            if not isinstance(data, nodetype.data_type.model_class()):
                raise TypeError("nodes of type %s require data of type %s, got: %s" % (nodetype, nodetype.data_type.model_class(), type(data)))
        elif data:
            raise TypeError("nodes of type %s may not carry data" % nodetype)
        return nodetype
        
    def create_node(self, nodetype=None, start=False, end=False, name='', data=None):
        nodetype = self._prep_nodetype(nodetype, data)
        return Node.objects.create(graph=self, node_type=nodetype, is_start_node=start, is_end_node=end, name=name, data=data or nodetype)
        
    def get_node(self, nodetype=None, start=False, end=False, name='', data=None):
        nodetype = self._prep_nodetype(nodetype, data)
        data = data or nodetype
        return Node.objects.get(
            graph=self, 
            node_type=nodetype, 
            is_start_node=start, 
            is_end_node=end, 
            name=name,
            data_id=data.pk, 
            data_ct=ContentType.objects.get_for_model(type(data)),
        )
        
    def create_workflow(self, **kwargs):
        workflow = Workflow.objects.create(graph=self, **kwargs)
        return workflow


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
    data_id = models.PositiveIntegerField(null=True)
    data_ct = models.ForeignKey(ContentType, null=True)
    data = GenericForeignKey(ct_field='data_ct', fk_field='data_id')
    outputs = models.ManyToManyField('self', related_name='inputs', through='Edge', symmetrical=False)
    is_start_node = models.BooleanField(default=False)
    is_end_node = models.BooleanField(default=False)

    def __unicode__(self):
        if self.name:
            return self.name
        return u"Node: %s" % (self.node_type)

    def add_edge(self, to, guard=None, negated=False, deadline=False):
        if guard:
            guard = guard._meta.instance
        return Edge.objects.create(from_node=self, to_node=to, guard=guard, negated=negated, deadline=deadline)
        
    def add_branches(self, guard, true, false):
        self.add_edge(true, guard=guard.instance)
        self.add_edge(false, guard=guard.instance, negated=True)
    
    def get_edge(self, to, guard=None, negated=False, deadline=False):
        if guard:
            guard = guard.instance
        return Edge.objects.get(from_node=self, to_node=to, guard=guard, negated=negated, deadline=deadline)
        
    def bind(self, workflow):
        return bind_node(self, workflow)


class Edge(models.Model):
    from_node = models.ForeignKey(Node, related_name='edges', null=True)
    to_node = models.ForeignKey(Node, related_name='incoming_edges', null=True)
    deadline = models.BooleanField(default=False)
    guard = models.ForeignKey(Guard, related_name='nodes', null=True)
    negated = models.BooleanField(default=False)
    
    def bind(self, workflow):
        return bind_edge(self, workflow)
        
    def bind_guard(self, workflow):
        return bind_guard(self, workflow)


class Workflow(models.Model):
    content_type = models.ForeignKey(ContentType)
    data_id = models.PositiveIntegerField()
    data = GenericForeignKey(ct_field='content_type', fk_field='data_id')
    graph = models.ForeignKey(Graph, related_name='workflows')
    is_finished = models.BooleanField(default=False)
    parent = models.ForeignKey('workflow.Token', null=True, related_name='parent_workflow')
    
    def clear_tokens(self):
        for token in self.tokens.filter(consumed_at=None):
            token.consume()

    def start(self):
        for node in self.graph.start_nodes:
            node.bind(self).receive_token(None)
        workflow_started.send(self)
        
    def finish(self, node=None):
        self.clear_tokens()
        self.is_finished = True
        self.save(force_update=True)
        workflow_finished.send(self)
        if self.parent:
            self.parent.node.bind(self.parent.workflow).progress(self.parent)
        

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
        self.node.bind(self.workflow).handle_deadline(self)
    
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
        
    def __unicode__(self):
        return u"%sToken at %s, deadline=%s, locked=%s" % (self.is_consumed and 'Consumed ' or '', self.node, self.deadline, self.locked)


import sys
if 'test' in sys.argv:
    class Foo(models.Model):
        flag = models.BooleanField(default=False)

        class Meta:
            app_label = 'workflow'
            
    class FooReview(models.Model):
        name = models.CharField(max_length=30)
        
        class Meta:
            app_label = 'workflow'
