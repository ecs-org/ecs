import datetime
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from ecs.workflow.models import Graph
from ecs.workflow.utils import make_dot
from ecs.core.models import Submission, Vote

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--model', dest='model', action='store', default=False, help="Don't change the db, just output what would be done"),
    )

    def handle(self, model=None, **options):
        model = {'Submission': Submission, 'Vote': Vote}.get(model)
        g = Graph.objects.get(model=model, auto_start=True)
        print make_dot(g)