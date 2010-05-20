####################################################
# Massimport for word documents of submissions
# This is experimental; don't use it.
####################################################

import sys
import os
import re
import BeautifulSoup
import chardet
import simplejson
from subprocess import Popen, PIPE
from optparse import make_option
from datetime import datetime, date

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from django.db.models import Q

from ecs.core import paper_forms
from ecs.core.models import Submission, SubmissionForm, Meeting, Participation


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--submission_dir', '-d', action='store', dest='submission_dir', help='import doc files of submissions from a directory'),
        make_option('--submission', '-s', action='store', dest='submission', help='import doc file of submission'),
        make_option('--timetable', '-t', action='store', dest='timetable', help='import timetable'),
        make_option('--participants', '-p', action='store', dest='participants', help='import participants from a file'),
        make_option('--date', '-b', action='store', dest='date', help='date for meeting start. e.g. 2010-05-18', default=str(date.today())),
    )

    def __init__(self, *args, **kwargs):
        self.filecount = 0
        self.importcount = 0
        self.failcount = 0
        super(Command, self).__init__(*args, **kwargs)

    def _abort(self, message, dont_exit=False):
        sys.stderr.write('\033[31mERROR: %s\033[0m\n' % message)
        sys.stderr.flush()
        if not dont_exit:
            sys.exit(1)

    def _warn(self, message):
        sys.stderr.write('\033[33m%s\033[0m' % message)
        sys.stderr.flush()

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

    def _print_stat(self, dont_exit_on_fail=False):
        print '== %d/%d documents imported ==' % (self.importcount - self.failcount, self.filecount)
        if self.failcount:
            self._abort('Failed to import %d files' % self.failcount, dont_exit=dont_exit_on_fail)
        else:
            print '\033[32mDone.\033[0m'

    @transaction.commit_on_success
    def _import_doc(self, filename):
        regex = re.match('(\d{2,4})_(\d{4})(_.*)?.doc', os.path.basename(filename))
        try:
            ec_number = '%s/%04d' % (regex.group(2), int(regex.group(1)))
        except IndexError:
            ec_number = re.match('(.*).doc', os.path.basename(filename)).group(1)

        antiword = Popen(['antiword', '-x', 'db', filename], stdout=PIPE, stderr=PIPE)
        docbook, standard_error = antiword.communicate()
        if antiword.returncode:
            raise Exception(standard_error.strip())
    
        s = BeautifulSoup.BeautifulStoneSoup(docbook)
    
        # look for paragraphs where a number is inside (x.y[.z])
        y = s.findAll('para', text=re.compile("[0-9]+\.[0-9]+(\.[0-9]+)*[^:]*:"), role='bold')

        data = []
        for a in y:
            # get number (fixme: works only for the first line, appends other lines unmodified)
            match = re.match('[^0-9]*([0-9]+\.[0-9]+(\.[0-9]+)*).*',a,re.MULTILINE)
            if not match:
                continue
            nr = match.group(1)

            parent = a.findParent()
            if parent.name == "entry":
                text= "\n".join(parent.string.splitlines()[2:])
            else:
                try:
                    text=unicode(a.findParent().find('emphasis', role='bold').contents[0])
                    # get parent (para), then get text inside emphasis bold, because every user entry in the word document is bold
                except AttributeError:
                    # have some trouble, but put all data instead inside for inspection
                    text="UNKNOWN:"+ unicode(a.findParent())

            text = text.strip()

            if text:
                data.append((nr, text,))

        fields = dict([(x.number, x.name,) for x in paper_forms.get_field_info_for_model(SubmissionForm) if x.number])
    
        create_data = {}
        for entry in data:
            try:
                key = fields[entry[0]]
                if key and not re.match(u'UNKNOWN:', entry[1]):
                    create_data[key] = entry[1]
            except KeyError:
                pass

        Submission.objects.filter(ec_number=ec_number).delete()
        submission = Submission.objects.create(ec_number=ec_number)

        create_data['submission'] = submission
        for key, value in (('subject_count', 1), ('subject_minage', 18), ('subject_maxage', 60)):
            if not key in create_data or not create_data[key].isdigit():
                create_data[key] = value

        SubmissionForm.objects.create(**create_data)

    def _import_files(self, files, dont_exit_on_fail=False):
        self.filecount = len(files)
        self._print_progress()
        warnings = ''
        for f in files:
            try:
                self._import_doc(f)
            except Exception, e:
                warnings += '== %s ==\n%s\n\n' % (os.path.basename(f), e)
                self.failcount += 1
            finally:
                self.importcount += 1
                self._print_progress()

        print ''
        if warnings:
            print ''
            self._warn(warnings)

        self._print_stat(dont_exit_on_fail=dont_exit_on_fail)

    def _import_file(self, filename):
        filename = os.path.expanduser(filename)
        if not os.path.isfile(filename):
            self._abort('"%s" does not exist' % filename)

        self._import_files([filename])

    def _import_dir(self, directory):
        path = os.path.expanduser(directory)
        if not os.path.isdir(path):
            self._abort('"%s" is not a directory' % path)

        files = [os.path.join(path, f) for f in os.listdir(path) if re.match('\d{2,4}_\d{4}(_.*)?.doc', f)]   # get all word documents in an existing directory
        files = [f for f in files if os.path.isfile(f)]   # only take existing files
        if not files:
            self._abort('No documents found in path "%s"' % path)

        self._import_files(files)

    def _import_timetable(self, filename, start):
        try:
            year, month, day = start.split('-')
        except ValueError:
            self.abort('please specify a date')

        filename = os.path.expanduser(filename)
        antiword = Popen(['antiword', '-x', 'db', filename], stdout=PIPE, stderr=PIPE)
        docbook, standard_error = antiword.communicate()
        if antiword.returncode:
            self._abort('Cant read file')

        s = BeautifulSoup.BeautifulStoneSoup(docbook)
        x=s.findAll(text=re.compile("EK Nr."))
        y=[a.next.strip().split("/") for a in x]
        documents = [os.path.join(os.path.dirname(filename), '%s_%s.doc' % (x[0], x[1])) for x in y]

        self._import_files(documents, dont_exit_on_fail=True)

        title = re.match('(.*).doc', os.path.basename(filename)).group(1)
        Meeting.objects.filter(title=title).delete()
        meeting = Meeting.objects.create(title=title, start=start)

        ec_numbers = ['%s/%04d' % (a[1], int(a[0])) for a in y]
        submission_count = len(ec_numbers)
        fail_count = 0
        for ec_number in ec_numbers:
            try:
                submission = Submission.objects.get(ec_number=ec_number)
                meeting.add_entry(submission=submission, duration_in_seconds=450)
            except Submission.DoesNotExist:
                fail_count += 1

        print '== %s/%s submission assigned to meeting ==' % (submission_count-fail_count, submission_count)

        if fail_count:
            self._abort('failed to assign %d submissions to the meeting' % fail_count)

    @transaction.commit_on_success
    def _import_participants(self, filename):
        filename = os.path.expanduser(filename)
        try:
            fd = open(filename, 'r')
        except IOError:
            self.abort('Cant open file %s' % filename)

        lines = [x.strip() for x in fd.readlines() if x.strip() and not x.strip().startswith('#')]  #filter out empty lines and commented lines
        fd.close()
        try:
            dataset = [(x.split(' ', 1)[0], x.split(' ', 1)[1].split(',')) for x in lines]
        except IndexError:
            self._abort('Syntax Error')

        while True:
            sys.stderr.write(' pk | title\n================\n')
            sys.stderr.write('\n'.join('%3d | %s' % (meeting.pk, meeting.title) for meeting in Meeting.objects.all()))
            try:
                meeting_pk = raw_input('\n\nWhich meeting(pk)? ')
            except KeyboardInterrupt:
                sys.stderr.write('\n')
                self._abort('quit')

            try:
                meeting = Meeting.objects.get(pk=meeting_pk)
                break
            except (Meeting.DoesNotExist, ValueError):
                self._warn('Meeting "%s" does not exist\n\n' % meeting_pk)

        print meeting
        print ''

        self.filecount = len(dataset)
        self._print_progress()
        warnings = ''
        for (username, ec_numbers) in dataset:
            username = username.lower()
            try:
                sid = transaction.savepoint()
                user = User.objects.get(Q(username=username)|Q(username__startswith=username)|Q(username__endswith=username))

                failed_ec_numbers = []
                for ec_number in ec_numbers:
                    try:
                        ec_number = '%04d' % int(ec_number)
                    except ValueError, e:
                        failed_ec_numbers.append(ec_number)
                        continue

                    try:
                        rofl = transaction.savepoint()
                        t_entry = meeting.timetable_entries.get(submission__ec_number__endswith=ec_number)
                        Participation.objects.create(entry=t_entry, user=user)
                    except Exception, e:
                        transaction.savepoint_rollback(rofl)
                        failed_ec_numbers.append(ec_number)
                        continue
                    else:
                        transaction.savepoint_commit(rofl)

                if failed_ec_numbers:
                    raise Exception('No sumbssions with ec_number: %s' % (', '.join(failed_ec_numbers)))


            except Exception, e:
                transaction.savepoint_rollback(sid)
                warnings += '== %s ==\n%s\n\n' % (username, e)
                self.failcount += 1
            else:
                transaction.savepoint_commit(sid)
            finally:
                self.importcount += 1
                self._print_progress()

        print ''
        if warnings:
            print ''
            self._warn(warnings)

        print '== %d/%d participants imported ==' % (self.importcount - self.failcount, self.filecount)
        if self.failcount:
            self._abort('Failed to import %d participants' % self.failcount)
        else:
            print '\033[32mDone.\033[0m'



    def handle(self, *args, **kwargs):
        options_count = sum([1 for x in [kwargs['submission_dir'], kwargs['submission'], kwargs['timetable'], kwargs['participants']] if x])
        if options_count is not 1:
            self._abort('please specifiy one of -d/-s/-t/-p')

        self._ask_for_confirmation()

        if kwargs['submission_dir']:
            self._import_dir(kwargs['submission_dir'])
        elif kwargs['submission']:
            self._import_file(kwargs['submission'])
        elif kwargs['timetable']:
            self._import_timetable(kwargs['timetable'], kwargs['date'])
        elif kwargs['participants']:
            self._import_participants(kwargs['participants'])

        sys.exit(0)


