#
%(pythonexedir)s/duply %(duplicity.duply_conf)s cleanup --force
%(pythonexedir)s/duply %(duplicity.duply_conf)s backup
%(pythonexedir)s/duply %(duplicity.duply_conf)s purge-full --force 

