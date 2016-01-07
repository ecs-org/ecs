import datetime, os, binascii

from django.core.urlresolvers import reverse
from django.conf import settings

from ecs.utils.testcases import LoginTestCase
from ecs.documents.models import Document, DocumentType


class DocumentsTest(LoginTestCase):
    '''Test for the Document module
    
    Tests for saving and retreiving documents via the Documents module.
    '''
    def test_download(self):
        '''Tests that a saved document can be downloaded,
        that its stored in the correct location and that it is a pdf.
        '''
        pdf_file = open(os.path.join(os.path.dirname(__file__), '..', 'core', 'tests', 'data', 'menschenrechtserklaerung.pdf'), 'rb')

        doctype = DocumentType.objects.create(name="Test")
        doc = Document.objects.create(version="1",
            date=datetime.date(2010, 0o3, 10), doctype=doctype)
        doc.store(pdf_file)
            
        response = self.client.get(reverse('ecs.documents.views.download_document', kwargs={'document_pk': doc.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(next(response.streaming_content)[:5], b'%PDF-')
