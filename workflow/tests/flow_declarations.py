from ecs.workflow import register, Activity, guard

from ecs.workflow.models import Foo, FooReview
from django.dispatch import Signal

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

def on_foo_change(sender, **kwargs):
    sender.workflow.unlock(D)
foo_change.connect(on_foo_change)

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
