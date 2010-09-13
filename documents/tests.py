import datetime, os
from django.core.files.base import File
from django.core.urlresolvers import reverse
from ecs.utils.testcases import LoginTestCase
from ecs.documents.models import Document, DocumentType


class DocumentsTest(LoginTestCase):
    def _create_document(self):
        doctype = DocumentType.objects.create(name="Test")
        # FIXME: where do we store test data?
        pdf_file = open(os.path.join(os.path.dirname(__file__), '..', 'core', 'tests', 'data', 'menschenrechtserklaerung.pdf'), 'rb')
        doc = Document(version="1", date=datetime.date(2010, 03, 10), doctype=doctype, file=File(pdf_file))
        doc.clean()
        doc.save()
        pdf_file.close()
        return doc
    
    def test_model(self):
        doc = self._create_document()
        self.failUnless(doc.file.name)

    def test_download(self):
        doc = self._create_document()
        response = self.client.get(reverse('ecs.documents.views.download_document', kwargs={'document_pk': doc.pk}))
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.content[:4], '%PDF')
        
    def test_upload(self):
        pass

