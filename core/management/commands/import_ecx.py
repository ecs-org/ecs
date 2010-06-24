import sys
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from ecs.core.models import Submission
from ecs.core.serializer import Serializer
from django.utils import simplejson
from StringIO import StringIO

class Command(BaseCommand):
    def handle(self, file, **options):
        serializer = Serializer()
        with open(file, 'rb') as f:
            serializer.read(f)
        

