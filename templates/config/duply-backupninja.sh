#
/usr/bin/duply %(duplicity.duply_conf)s cleanup --force
/usr/bin/duply %(duplicity.duply_conf)s backup
/usr/bin/duply %(duplicity.duply_conf)s purge-full --force

