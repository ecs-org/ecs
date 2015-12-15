# -*- coding: utf-8 -*-

from django.contrib import admin
from ecs.workflow.models import Graph, Node, Edge, Workflow, Token, NodeType, Guard

admin.site.register(Graph)
admin.site.register(Node)
admin.site.register(Edge)
admin.site.register(Workflow)
admin.site.register(Token)
admin.site.register(NodeType)
admin.site.register(Guard)

