#
duply %(duplicity.duply_conf)s cleanup --force
duply %(duplicity.duply_conf)s backup
duply %(duplicity.duply_conf)s purge-full --force 

