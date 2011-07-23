from django.test import TestCase
from django.core import management

class BootstrapTestCase(TestCase):
    '''Bootstrapping Tests
    
    Test for core bootstrapping functionality.
    '''
    
    def test_bootstrap(self):
        '''Tests if the application can execute the boostrap sequence for
        loading application an database presets
        '''
        
        management.call_command('bootstrap')
        