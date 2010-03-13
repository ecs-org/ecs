import datetime, os
from django.test import TestCase
from django.core.files.base import File
from ecs.core.models import Document, DocumentType

class DocumentsTest(TestCase):
    def _create_document(self):
        doctype = DocumentType.objects.create(name="Test")
        pdf_file = open(os.path.join(os.path.dirname(__file__), 'data', 'menschenrechtserklaerung.pdf'), 'rb')
        doc = Document(version="1", date=datetime.date(2010, 03, 10), doctype=doctype, file=File(pdf_file))
        doc.save()
        pdf_file.close()
        return doc
    
    def test_model(self):
        doc = self._create_document()
        self.failUnless(doc.file.name)

    def test_download(self):
        doc = self._create_document()
        response = self.client.get('/core/document/%s/download/' % doc.id)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.content[:4], '%PDF')
        
    def test_upload(self):
        pass

