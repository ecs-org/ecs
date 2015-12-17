from django.conf import settings
from celery.task import task

from ecs.utils.testcases import EcsTestCase

@task()
def basic_test():
    logger = basic_test.get_logger()
    logger.info("celery is running task, we write to the celery logger, and by the way, CELERY_ALWAYS_EAGER is %s" % str(settings.CELERY_ALWAYS_EAGER))
    return 'success'


class CeleryTest(EcsTestCase):
    '''Tests for Celery's asynchronous task queue.

Tests for accessibility and configuration of the asynchronous task queue.
'''
    
    def test_celery(self):
        '''Tests if the asynchronous task queue worker is accessible, if the logger works and if the remote test task succeeds.'''
        
        retval = basic_test.delay()
        self.assertEqual(retval.get(), 'success')
        self.assertEqual(retval.result, 'success')
        self.assertTrue(retval.successful())

