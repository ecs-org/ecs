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
        settings.CELERY_ALWAYS_EAGER = True
        settings.TESTING = True
        return super(EcsRunner, self).__init__(*args, **kwargs)


