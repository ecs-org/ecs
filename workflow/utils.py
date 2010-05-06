from ecs.workflow.models import NODE_TYPE_CATEGORY_SUBGRAPH, NODE_TYPE_CATEGORY_CONTROL, NODE_TYPE_CATEGORY_ACTIVITY

def make_dot(g, prefix='', embed_subgraphs=True, subgraph_id=''):
    common_edge_attrs = {'fontname': 'Helvetica', 'style': 'bold'}
    common_node_attrs = {'fontname': 'Helvetica'}
    
    statements = []
    def make_attrs(attrs):
        return ", ".join('%s="%s"' % (opt, val) for opt, val in attrs.iteritems())
        
    def add_node(node_id, **options):
        attrs = common_node_attrs.copy()
        attrs.update(options)
        statements.append('%sN_%s [%s]' % (prefix, node_id, make_attrs(attrs)))
        
    def add_edge(from_id, to_id, **options):
        attrs = common_node_attrs.copy()
        attrs.update(options)
        statements.append('%sN_%s -> %sN_%s [%s]' % (prefix, from_id, prefix, to_id, make_attrs(attrs)))
        
    add_node('%sStart' % subgraph_id, shape='circle', label='Start')
    add_node('%sEnd' % subgraph_id, shape='doublecircle', label='End')
    
    nodes = g.nodes.all()
    
    for node in nodes:
        opts = {
            'label': "%s: %s" % (node.pk, node.name or " ".join(node.node_type.name.rsplit('.', 1)[-1].split('_'))),
            'style': 'rounded',
            'shape': 'box',
        }
        
        if node.is_end_node:
            add_edge(node.pk, '%sEnd' % subgraph_id)
        if node.is_start_node:
            add_edge('%sStart' % subgraph_id, node.pk)
            
        if node.node_type.category == NODE_TYPE_CATEGORY_SUBGRAPH:
            statements.append(node.node_type.graph.dot(subgraph_id=node.pk))
            continue
        if node.node_type.category == NODE_TYPE_CATEGORY_CONTROL:
            opts.update({'color': 'lightblue'})
        if node.node_type.category == NODE_TYPE_CATEGORY_ACTIVITY:
            opts.update({'color': 'greenyellow'})
        add_node(node.pk, **opts)

    for node in nodes:
        for edge in node.edges.all():
            attrs = {}
            if edge.deadline:
                attrs['style'] = 'dotted'
            if edge.guard_id:
                label = " ".join(edge.guard.implementation.rsplit('.', 1)[-1].split('_'))
                add_node("E%s" % edge.pk, label='%s%s: %s' % (edge.negate and '~' or '', edge.guard_id, label), shape='plaintext')
                add_edge(edge.from_node_id, "E%s" % edge.pk, arrowhead='none', **attrs)
                add_edge("E%s" % edge.pk, edge.to_node_id, **attrs)
            else:
                add_edge(edge.from_node_id, edge.to_node_id, **attrs)
    if subgraph_id:
        graphtype = 'subgraph %sN%s' % (prefix, subgraph_id)
        statements.insert(0, 'rank=same')
    else:
        graphtype = 'digraph'
    return "%s{\n\t%s;\n}" % (graphtype, ";\n\t".join(statements))
