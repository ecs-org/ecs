import sys
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from ecs.core.models import Submission, SubmissionForm
from ecs.core.serializer import Serializer
from ecs.core import paper_forms

class FakeRequest(object):
    def __init__(self):
        self.META = {}

class Command(BaseCommand):
    def handle(self, ec_number, **options):
        try:
            s = Submission.objects.get(ec_number=ec_number)
        except Submission.DoesNotExist:
            raise CommandError("No submission matches the given EC-Number: %s" % ec_number)

        submission_form = s.get_most_recent_form()
        if not submission_form:
            raise CommandError("This submission does not have an attached SubmissionForm.")

        from ecs.core.views.utils import render_pdf
        pdf = render_pdf(FakeRequest(), 'db/submissions/xhtml2pdf/view.html', {
            'paper_form_fields': paper_forms.get_field_info_for_model(SubmissionForm),
            'submission_form': submission_form,
            'documents': submission_form.documents.filter(deleted=False).order_by('doctype__name', '-date'),
        })
        
        open('%s.pdf' % ec_number.replace('/', '-'), 'w').write(pdf)

