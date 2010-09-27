from datetime import timedelta

from ecs.workflow import Activity, register
from ecs.workflow.models import Foo

register(Foo)


class A(Activity):
    class Meta:
        model = Foo

class B(Activity):
    def is_repeatable(self):
        return True

    class Meta:
        model = Foo

class C(Activity):
    class Meta:
        model = Foo

class D(Activity):
    def is_reentrant(self):
        return False

    class Meta:
        model = Foo

class E(Activity):
    class Meta:
        model = Foo
