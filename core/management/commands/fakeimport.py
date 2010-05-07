import sys
import re
import BeautifulSoup
import chardet
import sys
import simplejson
from subprocess import Popen, PIPE

from django.core.management.base import BaseCommand

from ecs.core import paper_forms
from ecs.core.models import Submission, SubmissionForm


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        print "Disclaimer: This tool is NOT for production purposes!"
        print "Only use this for testing. You have been warned."
        if len(args) < 1:
            sys.stderr.write('Usage: %s %s [file]\n' % (sys.argv[0], sys.argv[1]))
            sys.exit(1)
    
    
        docbook = Popen(['antiword', '-x', 'db', args[0]], stdout=PIPE).communicate()[0]
    
        s = BeautifulSoup.BeautifulStoneSoup(docbook)
    
        # look for paragraphs where a number is inside (x.y[.z])
        y = s.findAll('para', text=re.compile("[0-9]+\.[0-9]+(\.[0-9]+)*[^:]*:"), role='bold')

        data = []
        for a in y:
            # get number (fixme: works only for the first line, appends other lines unmodified)
            match = re.match('[^0-9]*([0-9]+\.[0-9]+(\.[0-9]+)*).*',a,re.MULTILINE)
            if not match:
                continue
            nr = match.group(1)

            parent = a.findParent()
            if parent.name == "entry":
                text= "\n".join(parent.string.splitlines()[2:])
            else:
                try:
                    text=unicode(a.findParent().find('emphasis', role='bold').contents[0])
                    # get parent (para), then get text inside emphasis bold, because every user entry in the word document is bold
                except AttributeError:
                    # have some trouble, but put all data instead inside for inspection
                    text="UNKNOWN:"+ unicode(a.findParent())

            text = text.strip()

            if text:
                data.append((nr, text,))

        fields = dict([(x.number, x.name,) for x in paper_forms.get_field_info_for_model(SubmissionForm) if x.number])
    
        create_data = {}
        for entry in data:
            try:
                key = fields[entry[0]]
                if key and not re.match(u'UNKNOWN:', entry[1]):
                    create_data[key] = entry[1]
            except KeyError:
                pass

        create_data['submission'] = Submission.objects.create()
        for key, value in (('subject_count', 1), ('subject_minage', 18), ('subject_maxage', 60)):
            if not key in create_data:
                create_data[key] = value

        SubmissionForm.objects.create(**create_data)

