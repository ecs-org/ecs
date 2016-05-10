from django.core.management.base import BaseCommand
from django.apps import apps

from ecs.workflow.models import Graph
from ecs.workflow.utils import make_dot


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('model', help='The model name in app.Model syntax')

    def handle(self, **options):
        model = apps.get_model(options['model'])
        g = Graph.objects.get(model=model, auto_start=True)
        print(make_dot(g))
