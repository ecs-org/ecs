from ecs.workflow import control
# the following flow handlers are based on control pattern descriptions from http://www.workflowpatterns.com/patterns/control/

# Builtin:
# def parallel_split(node, workflow):
# def multi_choice(node, workflow):
# def simple_merge(node, workflow):

@control()
def generic(token):
    token.consume()
    token.node.progress(token.workflow)
    
@control()
def subgraph(token):
    node, workflow = token.node, token.workflow
    subworkflow = node.node_type.graph.start_workflow(data=workflow.data, parent=token)
    subworkflow.start()

@control()
def synchronization(token):
    node, workflow = token.node, token.workflow
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
#@control()
#def cancelling_discriminator(node, workflow):
#    pass

# nice to have
#@control()
#def thread_split(node, workflow):
#    pass

#@control()
#def thread_join(node, workflow):
#    pass