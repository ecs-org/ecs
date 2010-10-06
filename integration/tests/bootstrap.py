from django.test import TestCase
from django.core import management

class BootstrapTestCase(TestCase):
    def test_bootstrap(self):
        management.call_command('bootstrap')
        