from ecs.ecsmail.utils import whitewash
from ecs.utils.testcases import EcsTestCase

class PersilTest(EcsTestCase):
    testhtml = '<html><body><p>bla&auml;</p></body></html>'
    result_decoded_entities = u'bla\xe4'
    result_encoded_entities = u'bla&auml;'
    
    def testWhitewashing(self):
        self.assertEqual(whitewash(self.testhtml, True), self.result_decoded_entities)
        self.assertEqual(whitewash(self.testhtml, False), self.result_encoded_entities)
    
