import datetime
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from ecs.workflow.models import Graph
from ecs.workflow.utils import make_dot
from ecs.core.models import Submission, Vote
from ecs.meetings.models import Meeting
from ecs.notifications.models import Notification
from ecs.users.models import UserProfile

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--model', dest='model', action='store', default=False, 
            help="target model, can be one of Submission,Vote,Meeting,Notification,UserProfile"),
    )

    def handle(self, model=None, **options):
        model = {'Submission': Submission, 'Vote': Vote, 'Meeting': Meeting, 
            'Notification': Notification, 'UserProfile': UserProfile}.get(model)
        g = Graph.objects.get(model=model, auto_start=True)
        print make_dot(g)