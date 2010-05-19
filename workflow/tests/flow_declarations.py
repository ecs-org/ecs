from ecs import workflow
from ecs.workflow.models import Foo, FooReview
from django.dispatch import Signal

workflow.register(Foo)

foo_change = Signal()

@workflow.activity(model=Foo)
def A(token): pass

@workflow.activity(model=Foo)
def B(token): pass

@workflow.activity(model=Foo)
def C(token): pass

@workflow.activity(model=Foo, lock=lambda wf: wf.data.flag, signal=foo_change)
def D(token): pass

@workflow.activity(model=Foo)
def E(token): pass

@workflow.guard(model=Foo)
def GUARD(workflow):
    return workflow.data.flag
    
@workflow.activity(model=Foo, vary_on=FooReview)
def V(token): pass