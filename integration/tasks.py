from celery.decorators import task

@task()
def i_write_hello_world(alternatevalue=None, **kwargs):
    logger = i_write_hello_world.get_logger(**kwargs)
    logger.info("hello world execution")

    if alternatevalue:
        print alternatevalue
    else:
        print "Hello World"
