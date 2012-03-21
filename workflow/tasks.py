# dummy: see #4234

from celery.decorators import task

@task()
def handle_deadlines():
    pass
