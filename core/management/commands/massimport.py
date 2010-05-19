####################################################
# Massimport for word documents of submissions
# This is experimental; don't use it.
####################################################

import sys
import os

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        self.filecount = 0
        self.importcount = 0
        super(Command, self).__init__(*args, **kwargs)

    def _abort(self, message):
        sys.stderr.write('\033[31mERROR:\033[0m %s\n' % message)
        sys.stderr.flush()
        sys.exit(1)

    def _ask_for_confirmation(self):
        print "DISCLAIMER: This tool is NOT for production purposes!" # right
        print "Only use this for testing. You have been warned."
        userinput = raw_input('Do you want to continue? (yes/NO): ')
        print ''
        if not userinput.lower() == 'yes':
            self._abort('confirmation failed')

    def _print_progress(self):  # MAGIC
        BARWIDTH = 70
        a = int(round(float(BARWIDTH)/self.filecount*self.importcount))
        b = BARWIDTH - a
        sys.stdout.write('\r[%s%s%s] %3d/%3d ' % (('='*(a-1)), ('>' if not self.importcount == self.filecount else '='), (' '*b), self.importcount, self.filecount))
        sys.stdout.flush()

    def _print_stat(self):
        print '== %d/%d documents imported ==' % (self.importcount, self.filecount)
        if not self.importcount == self.filecount:
            self._abort('Failed to import %d files' % (self.filecount - self.importcount))
        else:
            print '\033[32mDone\033[0m'

    def handle(self, *args, **kwargs):
        self._ask_for_confirmation()
        if len(args) < 1:
            sys.stderr.write('Usage: %s %s [path]\n' % (sys.argv[0], sys.argv[1]))
            sys.exit(1)

        path = os.path.expanduser(sys.argv[2])
        if not os.path.isdir(path):
            self._abort('"%s" is not a directory' % path)

        files = [os.join(path, f) for f in os.listdir(path) if f.endswith('.doc')]   # get all word documents in an existing directory
        files = [f for f in files if os.path.isfile(f)]   # only take existing files
        if not files:
            self._abort('No documents found in path "%s"' % path)

        self.filecount = len(files)
        self._print_progress()
        for f in files:
            # FIXME: dont use an external command
            try:
                os.system('./manage.py fakeimport %s' % f)
            except Exception, e:
                raise e
            else:
                self.import_count += 1
                self._print_progress()

        self._print_stat()
        sys.exit(0)


