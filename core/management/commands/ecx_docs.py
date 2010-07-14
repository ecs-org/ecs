import sys
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import get_template
from django.template import Context

from ecs.core.models import Submission
from ecs.core.serializer import Serializer


class Command(BaseCommand):
    def handle(self, **options):
        ecxf = Serializer()
        tpl = get_template('docs/ecx/base.html')
        print tpl.render(Context({
            'version': ecxf.version,
            'fields': ecxf.docs(),
        })).encode('utf-8')
         
        

