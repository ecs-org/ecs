import os, subprocess
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction


class Command(BaseCommand):
    @transaction.commit_manually
    def handle(self, dirname, **options):
        from ecs.documents.models import Document, DocumentType
        from ecs.documents.forms import DocumentForm
        dt = DocumentType.objects.order_by('pk')[0:1][0]
        try:
            for path in os.listdir(dirname):
                if not path.lower().endswith('.pdf'):
                    continue
                print "-" * 80
                print "source:", path
                path = os.path.join(dirname, path)
                size = os.path.getsize(path)
                with open(path, 'rb') as f:
                    try:
                        form = DocumentForm({
                            'version': 'test',
                            'date': '11.11.2011',
                            'name': 'test.pdf',
                            'doctype': dt.pk,
                        }, {'file': UploadedFile(f, 'test.pdf', 'application/pdf', size, None)})
                        if form.is_valid():
                            form.save()
                            print "... ok"
                        else:
                            for field, messages in form.errors.iteritems():
                                print "%s: %s" % (field, ", ".join(unicode(msg) for msg in messages))
                    except Exception as e:
                        print "... unexpected error", type(e), e
                    
        finally:
            transaction.rollback()