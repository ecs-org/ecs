from django.conf import settings
#from django.test.simple import run_tests as run_tests_orig
from django_nose.runner import run_tests as run_tests_orig

USAGE = """\
Custom ecs test runner to allow testing of all ecs related tasks
 eg. celery delayed tasks.
"""

def run_tests(test_labels, *args, **kwargs):
    """Django test runner allowing testing of ecs.

    All tasks are run locally, not in a worker.
        TEST_RUNNER = "utils.ecs_runner.run_tests"

    """

    settings.CELERY_ALWAYS_EAGER = True
    return run_tests_orig(test_labels, *args, **kwargs)
