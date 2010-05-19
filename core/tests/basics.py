from ecs.utils.testcases import LoginTestCase

def test_import():
    "test if the urls module and the views are importable"
    import ecs.urls
    import ecs.core.urls
    import ecs.core.views
    import ecs.core.models
    
class CoreUrlsTest(LoginTestCase):
    def test_index(self):
        response = self.client.get('/core/')
        self.failUnlessEqual(response.status_code, 302)

    def test_index(self):
        response = self.client.get('/dashboard/')
        self.failUnlessEqual(response.status_code, 200)
        
    def test_submission_form_new(self):
        response = self.client.get('/core/submission_form/new/')
        self.failUnlessEqual(response.status_code, 302)

    def test_notification_new(self):
        response = self.client.get('/core/notification/new/')
        self.failUnlessEqual(response.status_code, 200)

    def test_notifications(self):
        response = self.client.get('/core/notifications/')
        self.failUnlessEqual(response.status_code, 200)

    def test_submission_forms(self):
        response = self.client.get('/core/submission_forms/')
        self.failUnlessEqual(response.status_code, 200)
