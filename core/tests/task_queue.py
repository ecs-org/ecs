from django.test import TestCase

from celery.decorators import task

@task()
def basic_test():
    return 'success'

class CeleryTest(TestCase):
    def test_celery(self):
        retval = basic_test.delay()
        self.failUnlessEqual(retval.get(), 'success')
        self.failUnlessEqual(retval.result, 'success')
        self.failUnless(retval.successful())

