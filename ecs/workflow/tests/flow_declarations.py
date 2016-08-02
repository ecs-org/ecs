from django.dispatch import Signal, receiver

from ecs.workflow import register, Activity, guard
from ecs.workflow.tests.models import Foo, FooReview
from ecs.workflow.patterns import Generic

register(Foo)

foo_change = Signal()

class A(Activity):
    class Meta:
        model = Foo

class B(Activity):
    class Meta:
        model = Foo

class C(Activity):
    class Meta:
        model = Foo

class D(Activity):
    def is_locked(self):
        return not self.workflow.data.flag
        
    class Meta:
        model = Foo
        signals = (foo_change,)

class F(Generic):
    def is_locked(self):
        return not self.workflow.data.flag

    class Meta:
        model = Foo
        signals = (foo_change,)

@receiver(foo_change)
def on_foo_change(sender, **kwargs):
    sender.workflow.unlock(D)
    sender.workflow.unlock(F)

class E(Activity):
    class Meta:
        model = Foo

@guard(model=Foo)
def GUARD(workflow):
    return workflow.data.flag

class V(Activity):
    class Meta:
        model = Foo
        vary_on = FooReview
