from django.conf import settings
from django_nose.runner import NoseTestSuiteRunner

USAGE = """\
Custom ecs test runner to allow testing of all ecs related tasks
 eg. celery delayed tasks.
"""

class EcsRunner(NoseTestSuiteRunner):
    """Django test runner allowing testing of ecs.

    sets settings.TESTING = True (for workaround in tests)
    All tasks are run locally, not in a worker.
        TEST_RUNNER = "ecs.utils.ecs_runner.EcsRunner"

    """
    def __init__(self, *args, **kwargs):
        #TODO: for other dirty hacks before we do even more dirty hacks, can be used to do workaround daemons in testing that are not here
        settings.TESTING = True
        return super(EcsRunner, self).__init__(*args, **kwargs)


