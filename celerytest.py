from celery.decorators import task

@task()
def i_write_hello_world(alternatevalue=None):
    if alternatevalue:
        print alternatevalue
    else:
        print "Hello World"
