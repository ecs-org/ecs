from django.test import TestCase
from django.core import management


class SanityTests(TestCase):
    def test_import(self,):
        '''
        Test if settings and urls modules are importable.
        Simple but quite useful.
        '''
        from ecs import settings
        from ecs import urls

    def test_bootstrap(self):
        '''
        Tests if the application can execute the boostrap sequence for
        loading application an database presets
        '''
        management.call_command('bootstrap')
