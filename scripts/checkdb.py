#!/usr/bin/env python

import os, sys, importlib

try:
  import psycopg2
  import dj_database_url
except ImportError as e:
  print("ERROR: fatal, could not import: {0}".format(e))
  usage()

def usage():

  print('''
usage: {0} connect db_host db_name db_user db_pass
 or  : {0} url "postgres://db_user:db_pass@db_host/db_name"
 or  : {0} import "ecs.settings"

program will exit with code:

 0 = connected to database, and has django_migrations
 1 = connected to database, and has south_migrationhistory
 2 = connected to database, but no migrations where found, empty database ?

 8 = connected to server but not to database
 9 = could not connect to server
10 = wrong/empty parameter, missing library, other fatal errors

  '''.format(sys.argv[0]))
  sys.exit(10)


def parse_args():

  if len(sys.argv) < 3:
    usage()

  cmd =sys.argv[1].lower()

  if cmd not in ('connect', 'url', 'import') or \
    (len(sys.argv) == 6 and cmd != 'connect'):
    usage()

  if cmd == "connect":
    ret= sys.argv[2:]
    return ret

  if cmd == "url":
    try:
      db = dj_database_url.config()
    except Exception as e:
      print('could not parse DATABASE_URL')
      sys.exit(10)

  else:
    try:
      sys.path.insert(0, os.getcwd())
      settings = importlib.import_module(sys.argv[2])
      db = settings.DATABASES['default']
    except ImportError as e:
      print('could not import settings, error={0}'.format(e))
      sys.exit(10)

  ret = (db.get('HOST', ''),
      db.get('NAME', ''),
      db.get('USER', ''),
      db.get('PASSWORD', ''))

  return ret


def main():

  (DB_HOST, DB_NAME, DB_USER, DB_PASS) = parse_args()

  try:
    conn = psycopg2.connect("dbname='" + DB_NAME + "' user='" + DB_USER + "' host='" + DB_HOST + "' password='" + DB_PASS + "'")

  except psycopg2.Error as e:
    if e.args[0].endswith('does not exist\n'):
      print('database named "{0}" does not exist'.format(DB_NAME))
      sys.exit(8)

    print('could not connect to database server error was {0}'.format(e))
    sys.exit(9)

  has_django_migrations = False
  has_south_migrations = False

  try:
    with conn.cursor() as cur:
      cur.execute("select * from information_schema.tables where table_name=%s", ('django_migrations',))
      has_django_migrations = cur.rowcount > 0

    with conn.cursor() as cur:
      cur.execute("select * from information_schema.tables where table_name=%s", ('south_migrationhistory',))
      has_south_migrations = cur.rowcount > 0

  finally:
    conn.close()

  if has_django_migrations:
    print('django_migrations found')
    sys.exit(0)

  if has_south_migrations:
    print('south_migrationhistory found')
    sys.exit(1)

  print('neither django_migrations nor south_migrationhistory found, database empty ?')
  sys.exit(2)


if __name__ == '__main__':
    main()
