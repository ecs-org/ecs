import datetime, os, binascii
from django.core.files.base import File
from django.core.urlresolvers import reverse
from django.conf import settings
from ecs.utils.testcases import LoginTestCase
from ecs.utils.pathutils import tempfilecopy
from ecs.documents.models import Document, DocumentType


class DocumentsTest(LoginTestCase):
    
    def test_download(self):
        self.pdf_magic = binascii.a2b_hex('255044462D31')         
        self.tempfilename = tempfilecopy(open(os.path.join(os.path.dirname(__file__), '..', 'core', 'tests', 'data', 'menschenrechtserklaerung.pdf'), 'rb'))
        self.doctype = DocumentType.objects.create(name="Test")
        self.pdf_file = open(self.tempfilename, 'rb')
        self.pdf_data = self.pdf_file.read()
        self.doc = Document(version="1", date=datetime.date(2010, 03, 10), doctype=self.doctype, file=File(self.pdf_file))
        self.doc.save()
            
        self.failUnless(self.doc.file.name)
        response = self.client.get(reverse('ecs.documents.views.download_document', kwargs={'document_pk': self.doc.pk}))
        self.assertEqual(response.status_code, 302)
        url = response['Location']
        self.assertTrue(url.startswith(settings.MS_CLIENT["server"]))
        url = url [len(settings.MS_CLIENT["server"]):]
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        current_magic = response.content[:len(self.pdf_magic)]
        self.assertTrue(current_magic == self.pdf_magic)
        
    def test_upload(self):
        pass

