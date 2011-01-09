import os

from windmill.authoring import WindmillTestClient
from windmill.authoring.djangotest import WindmillDjangoUnitTest

class WindmillTest(WindmillDjangoUnitTest): 
        
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"main", "anonymous")
    browser = 'firefox'
    
    def setUp(self):
        from django.core import management
        management.call_command('bootstrap')
        super(WindmillTest, self).setUp()
        
class authWindmillTest(WindmillTest):
    
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"main", "logged_in")
    
    def setUp(self):
        super(authWindmillTest, self).setUp()
        client = WindmillTestClient(__name__)

        client.click(id=u'id_username')
        client.type(text=u'windmill@example.org', id=u'id_username')
        client.click(id=u'id_password')
        client.type(text=u'shfnajwg9e', id=u'id_password')
        client.click(value=u'login')
        client.waits.forPageLoad(timeout=u'20000')
    
    def tearDown(self):    
        client = WindmillTestClient(__name__)
        
        client.waits.forElement(link=u'Logout', timeout=u'8000')
        client.click(link=u'Logout')
        client.waits.forPageLoad(timeout=u'20000')
        client.waits.forElement(link=u'login')
        
        super(authWindmillTest, self).tearDown()


