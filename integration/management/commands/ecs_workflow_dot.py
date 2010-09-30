import datetime

from django.core.management.base import BaseCommand, CommandError

from ecs.workflow.models import Graph
from ecs.workflow.utils import make_dot
from ecs.core.models import Submission

class Command(BaseCommand):
    def handle(self, **options):
        g = Graph.objects.get(model=Submission, auto_start=True)
        print make_dot(g)