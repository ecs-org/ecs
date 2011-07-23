from django.core.urlresolvers import reverse
from ecs.utils.testcases import LoginTestCase, EcsTestCase

class ImportTest(EcsTestCase):
    ''' Check if base and core urls,view,models are importable '''
    
    def test_import(self):
        "test if the urls module and the views are importable"
        
        import ecs.urls
        import ecs.core.urls
        import ecs.core.views
        import ecs.core.models
        
class CoreUrlsTest(LoginTestCase):
    '''Class for testing '''
    
    def test_index(self):
        '''Tests if the Dashboard/main-site of the system is accessible.'''
        
        response = self.client.get(reverse('ecs.dashboard.views.view_dashboard'))
        self.failUnlessEqual(response.status_code, 200)
        
    def test_submission_forms(self):
        '''Tests if the all-submissions view of the system is accessible.'''
        
        response = self.client.get(reverse('ecs.core.views.all_submissions'))
        self.failUnlessEqual(response.status_code, 200)

