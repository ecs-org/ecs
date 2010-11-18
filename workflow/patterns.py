from ecs.workflow.controllers import FlowController
# the following flow handlers are based on control pattern descriptions from http://www.workflowpatterns.com/patterns/control/
# builtin patterns: ParallelSplit, MultiChoice, SimpleMerge

class Generic(FlowController):
    def handle_token(self, token):
        self.progress(token)

class Subgraph(FlowController):
    def handle_token(self, token):
        subworkflow = self.node.node_type.graph.create_workflow(data=self.workflow.data, parent=token)
        subworkflow.start()

class Synchronization(FlowController):
    def handle_token(self, token):
        tokens = self.get_tokens().select_related('source')
        expected_inputs = set(self.node.inputs.all())
        synchronized_tokens = set()
        if len(tokens) >= len(expected_inputs):
            for t in tokens:
                if t.source in expected_inputs:
                    expected_inputs.remove(t.source)
                    synchronized_tokens.add(t)
            if not expected_inputs:
                self.progress(*synchronized_tokens)


### nice to have
#class CancellingDiscriminator(FlowController):
#    def handle_token(self, token):
#        pass
#class ThreadSplit(FlowController):
#    def handle_token(self, token):
#        pass
#class ThreadJoin(FlowController):
#    def handle_token(self, token):
#        pass
