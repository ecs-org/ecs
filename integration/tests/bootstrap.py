from django.test import TestCase
from django.core import management

class BootstrapTestCase(TestCase):
    '''Bootstrap Tests'''
    
    def test_bootstrap(self):
        '''Tests if the bootstrap mechanism works'''
        
        management.call_command('bootstrap')
        