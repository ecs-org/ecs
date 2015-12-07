logrotate_targets = {
    'default': '*.log'
}

upstart_targets = {
    'celeryd': (None, './manage.py celeryd -l warning -f ../../ecs-log/celeryd.log'),
    'celerybeat': (None, './manage.py celerybeat -S djcelery.schedulers.DatabaseScheduler -l warning -f ../../ecs-log/celerybeat.log'),
    'ecsmail': (None, './manage.py ecsmail server ../../ecs-log/ecsmail.log'),
    'mocca': ('upstart-tomcat.conf', ''),
    'pdfas': ('upstart-tomcat.conf', ''),
}

test_flavors = {
    'default': './manage.py test',
    'mainapp': './manage.py test',
    'mediaserver': 'false',  # include in the mainapp tests
    'mailserver': 'false', # included in the mainapp tests
}
