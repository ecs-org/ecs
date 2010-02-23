from django.test import TestCase

from ecs.utils.htmldoc import htmldoc

class HtmldocTest(TestCase):
	def test_simple(self):
		pdf = htmldoc('<html><body>Test</body></html>', webpage=True)
		self.failUnlessEqual(pdf[:4], "%PDF")
