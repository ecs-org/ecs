import sys
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from ecs.core.models import Submission
from ecs.core.serializer import Serializer
from django.utils import simplejson
from StringIO import StringIO

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-o', action='store', dest='out', help='output file', default=None),
    )
    def handle(self, ec_number, **options):
        try:
            s = Submission.objects.get(ec_number=ec_number)
        except Submission.DoesNotExist:
            raise CommandError("No submission matches the given EC-Number: %s" % ec_number)

        sf = s.get_most_recent_form()
        if not sf:
            raise CommandError("This submission does not have an attached SubmissionForm.")

        f = file(options['out'] or "%s.ecx" % ec_number.replace('/', '-'), 'w')
        ecxf = Serializer()
        ecxf.write(sf, f)
        f.close()
        

