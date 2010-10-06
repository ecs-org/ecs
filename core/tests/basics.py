from django.core.urlresolvers import reverse
from ecs.utils.testcases import LoginTestCase

def test_import():
    "test if the urls module and the views are importable"
    import ecs.urls
    import ecs.core.urls
    import ecs.core.views
    import ecs.core.models
    
class CoreUrlsTest(LoginTestCase):
    def test_index(self):
        response = self.client.get(reverse('ecs.dashboard.views.view_dashboard'))
        self.failUnlessEqual(response.status_code, 200)
        
    def test_submission_forms(self):
        response = self.client.get(reverse('ecs.core.views.submission_form_list'))
        self.failUnlessEqual(response.status_code, 200)
