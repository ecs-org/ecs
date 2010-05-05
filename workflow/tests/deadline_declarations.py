from datetime import timedelta

from ecs import workflow
from ecs.workflow.models import Foo

workflow.register(Foo)

@workflow.activity(model=Foo, deadline=timedelta(seconds=0))
def A(token): pass

@workflow.activity(model=Foo)
def B(token): pass

@workflow.activity(model=Foo)
def C(token): pass
