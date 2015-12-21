from ecs.ecsmail.utils import whitewash
from ecs.utils.testcases import EcsTestCase

class PersilTest(EcsTestCase):
    '''Class for Testing the Sanitizing of strings containing html entities.
    
    '''
    
    testhtml = '<html><body><p>bla&auml;</p></body></html>'
    result_decoded_entities = u'bla\xe4'
    
    def testWhitewashing(self):
        '''Tests if Html entities are translated correctly
        
        '''
        
        self.assertEqual(whitewash(self.testhtml), self.result_decoded_entities)
