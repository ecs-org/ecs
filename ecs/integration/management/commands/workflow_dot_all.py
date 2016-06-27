from itertools import groupby
import difflib
import subprocess
import zipfile

from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from ecs.tasks.models import Task, TaskType
from ecs.workflow.models import Graph
from ecs.workflow.utils import make_dot


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-o', '--out', help='Output file (zip)')
        parser.add_argument('model', help='The model name in app.Model syntax')

    def handle(self, **options):
        model = apps.get_model(options['model'])
        model_name = model._meta.model_name

        task_types = TaskType.objects.filter(
            id__in=Task.objects.open().values('task_type'))
        graphs = Graph.objects.filter(
            Q(nodes__in=task_types.values('workflow_node')) | Q(auto_start=True),
            content_type=ContentType.objects.get_for_model(model)
        ).distinct().order_by('id')

        def _key(g):
            s = []
            for node in g.nodes.all():
                try:
                    group = node.tasktype.group.name if node.tasktype.group else ''
                except TaskType.DoesNotExist:
                    group = ''

                s.append('N {} impl={} group={} start={} end={}'.format(
                    node.uid,
                    node.node_type.implementation,
                    group,
                    node.is_start_node,
                    node.is_end_node,
                ))

                for edge in node.edges.all():
                    s.append('E {} -> {} neg={} impl={}'.format(
                        edge.from_node.uid,
                        edge.to_node.uid,
                        edge.negated,
                        edge.guard.implementation if edge.guard else '',
                    ))

            s.sort()
            return '\n'.join(s) + '\n'


        grouped = [list(graphs) for key, graphs in groupby(graphs, _key)]

        out = options['out'] or '{}.zip'.format(model_name)
        with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for graphs in grouped:
                last = graphs[-1]

                p = subprocess.Popen(['dot', '-Tpng'],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                png, stderr = p.communicate(make_dot(last).encode('ascii'))
                zf.writestr('{}/{}.png'.format(model_name, last.id), png)

                tasks = (Task.objects
                    .filter(task_type__workflow_node__graph__in=graphs)
                    .order_by('created_at'))

                stats = 'Tasks open={} closed={}'.format(tasks.open().count(),
                    tasks.exclude(closed_at=None).count())
                if tasks:
                    open_tasks = list(tasks.open())
                    stats += ' first={} last={}'.format(
                        open_tasks[0].created_at.strftime('%Y-%m-%d'),
                        open_tasks[-1].created_at.strftime('%Y-%m-%d'),
                    )

                zf.writestr('{}/{}.txt'.format(model_name, last.id),
                    (stats + '\n\n' + _key(last)).encode('ascii'))

            for e1, e2 in zip(grouped, grouped[1:]):
                key1 = _key(e1[0]).splitlines(keepends=True)
                key2 = _key(e2[0]).splitlines(keepends=True)
                diff = ''.join(difflib.unified_diff(key1, key2,
                    '{}/{}.txt'.format(model_name, e1[-1].id),
                    '{}/{}.txt'.format(model_name, e2[-1].id)))
                zf.writestr(
                    '{}/{}-{}.diff'.format(model_name, e1[-1].id, e2[-1].id),
                    diff.encode('ascii'))
