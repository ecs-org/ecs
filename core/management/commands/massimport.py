# -*- coding: utf-8 -*-
####################################################
# Massimport for word documents of submissions
# This is experimental; don't use it.
####################################################

import sys
import os
import re
import math
import platform
from subprocess import Popen, PIPE
from optparse import make_option
from datetime import datetime, date
from mpmath import mp, mpf

import BeautifulSoup
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.files import File
from django.conf import settings

from ecs.core import paper_forms
from ecs.core.models import Submission, SubmissionForm, MedicalCategory
from ecs.meetings.models import Meeting, Participation
from ecs.documents.models import Document, DocumentType


PLATFORM = 'unix'
if platform.platform().lower().startswith('win'):
    PLATFORM = 'win'
    
def _popen_antiword(filename):
    return Popen(['antiword'] + getattr(settings, 'ANTIWORD_ARGS', []) + ['-x', 'db', filename], stdout=PIPE, stderr=PIPE)

class ProgressBar():
    def __init__(self, minimum=0, maximum=100):
        self.minimum = minimum
        self.maximum = maximum
        self.barwidth = None

    def update(self, current):
        if not PLATFORM == 'win':
            try:
                import termios, fcntl, struct
                s = struct.pack("HHHH", 0, 0, 0, 0)
                fd_stdout = sys.stderr.fileno()
                x = fcntl.ioctl(fd_stdout, termios.TIOCGWINSZ, s)
                self.barwidth = struct.unpack("HHHH", x)[1]
            except:
                self.barwidth = None
    
        if not self.barwidth:
            sys.stdout.write(
                '.' if not current % 10 == 0 else '%d/%s' % (current, self.maximum)
            )
            sys.stdout.flush()
            return
        
        a = int(round(float(self.barwidth-14)/(self.maximum - self.minimum)*current))
        b = (self.barwidth-14) - a
        
        sys.stderr.write('\r[%s%s%s] %4d/%4d ' % (
            ('='*(a-1)),
            ('>' if not current == self.maximum else '='),
            (' '*b), current, self.maximum
        ))
        sys.stderr.flush()


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--submission_dir', '-d', action='store', dest='submission_dir', help='import doc files of submissions from a directory'),
        make_option('--submission', '-s', action='store', dest='submission', help='import doc file of submission'),
        make_option('--timetable', '-t', action='store', dest='timetable', help='import timetable'),
        make_option('--categorize', '-c', action='store', dest='categorize', help='import medical categories from a file'),
        make_option('--participants', '-p', action='store', dest='participants', help='import participants from a file'),
        make_option('--date', '-b', action='store', dest='date', help='date for meeting start. e.g. 2010-05-18', default=str(date.today())),
        make_option('--analyze', '-a', action='store', dest='analyze_dir', help='analyze a bunch of doc files'),
        make_option('--meeting_dates', '-m', action='store', dest='meeting_dates', help='import meeting dates from .py file'),
    )

    def _abort(self, message, dont_exit=False):
        if PLATFORM == 'win':
            sys.stderr.write('%s' % message)
        else:
            sys.stderr.write('\033[31mERROR: %s\033[0m\n' % message)
        sys.stderr.flush()
        
        if not dont_exit:
            sys.exit(1)

    def _warn(self, message):
        if PLATFORM == 'win':
            sys.stderr.write('%s' % message)
        else:
            sys.stderr.write('\033[33m%s\033[0m' % message)
        sys.stderr.flush()

    def _parse_doc(self, filename):
        regex = re.match('(\d{1,4})_(\d{4})(_.*)?.doc', os.path.basename(filename))
        basename = re.match('(.*).doc', os.path.basename(filename)).group(1)
        try:
            ec_number = '%s%04d' % (regex.group(2), int(regex.group(1)))
        except IndexError:
            ec_number = basename
        
        
        documents = []
        dirname = os.path.dirname(filename)
        for document in os.listdir(dirname):
            match = re.match(r'%s-((Patienteninformation)|(.*Lebenslauf).*)\.pdf' % basename, document)
            
            if not match:
                continue
            
            doctype_str = 'Patienteninformation' if match.group(2) else "Curriculum Vitae (CV)"
            doctype = DocumentType.objects.get(name=doctype_str)

            documents.append({
                'title': match.group(1),
                'mimetype': 'application/pdf',
                'filename': os.path.join(dirname, document),
                'doctype': doctype,
            })

        antiword = _popen_antiword(filename)
        docbook, standard_error = antiword.communicate()
        if antiword.returncode:
            raise Exception(standard_error.strip())
    
        s = BeautifulSoup.BeautifulStoneSoup(docbook)
    
        # look for paragraphs where a number is inside (x.y[.z])
        y = s.findAll('para', text=re.compile(r'\d+(\.\d+)+\.?\s+'), role='bold')

        data = []
        for a in y:
            # get number (fixme: works only for the first line, appends other lines unmodified)
            match = re.match(r'\D*(\d+(\.\d+)+).*',a,re.MULTILINE)
            if not match:
                continue
            nr = match.group(1)

            parent = a.findParent()
            if parent.name == "entry":
                text= "\n".join(parent.string.splitlines()[2:])
            else:
                try:
                    b = parent.find('emphasis', role='bold')
                    if not b:
                        b = parent.findNextSibling('para').findChild('emphasis', role='bold')
                    
                    text=unicode(b.contents[0])

                except AttributeError:
                    #print '\n%s' % nr
                    # have some trouble, but put all data instead inside for inspection
                    text="UNKNOWN:"+ unicode(a.findParent())

            text = text.strip()

            if text:
                data.append((nr, text,))

        fields = dict([(x.number, x.name,) for x in paper_forms.get_field_info_for_model(SubmissionForm) if x.number and x.name])
    
        submissionform_data = {}
        for entry in data:
            try:
                key = fields[entry[0]]
                if key and not re.match(u'UNKNOWN:', entry[1]):
                    submissionform_data[key] = entry[1]
            except KeyError:
                pass

        submission_data = {
            'ec_number': ec_number,
        }

        return (submission_data, submissionform_data, documents)

    @transaction.commit_on_success
    def _import_doc(self, filename):
        submission_data, submissionform_data, documents = self._parse_doc(filename)
        submission, created = Submission.objects.get_or_create(**submission_data)
        
        for key, value in (('subject_count', 1), ('subject_minage', 18), ('subject_maxage', 60)):
            if not key in submissionform_data or not submissionform_data[key].isdigit():
                submissionform_data[key] = value
        
        # TODO: do not ignore this and fix it
        for key in submissionform_data.keys():
            if hasattr(SubmissionForm, key):
                del submissionform_data[key]
        
        submissionform_data['submission'] = submission
        submission_form = SubmissionForm.objects.create(**submissionform_data)
        
        for d in documents:
            pdf_file = open(d['filename'], 'rb')
            doc = Document(
                version=d['title'],
                date=datetime.now(),
                doctype=d['doctype'],
                mimetype=d['mimetype'],
                file=File(pdf_file)
            )
            doc.save()
            submission_form.documents.add(doc)
        
    
    def _import_files(self, files, dont_exit_on_fail=False):
        failcount = 0
        importcount = 0
    
        import traceback
        pb = ProgressBar(maximum=len(files))
        pb.update(importcount)
        
        warnings = ''
        for f in files:
            try:
                self._import_doc(f)
            except Exception, e:
                warnings += '== %s ==\n%s\n\n' % (os.path.basename(f), e)
                failcount += 1
            finally:
                importcount += 1
                pb.update(importcount)

        print ''
        if warnings:
            print ''
            self._warn(warnings)
        
        if failcount:
            self._abort('Failed to import %d files' % failcount, dont_exit=dont_exit_on_fail)
    
    def _analyze_dir(self, directory):
        path = os.path.expanduser(directory)
        if not os.path.isdir(path):
            self._abort('"%s" is not a directory' % path)

        files = [os.path.join(path, f) for f in os.listdir(path) if re.match('\d{1,4}_\d{4}(_.*)?.doc', f)]
        files = [f for f in files if os.path.isfile(f)]
        if not files:
            self._abort('No documents found in path "%s"' % path)

        data = {}
        for field in paper_forms.get_field_info_for_model(SubmissionForm):
            if field.number and field.name:
                data[field.name] = []

        failcount = 0
        importcount = 0
        
        pb = ProgressBar(maximum=len(files))
        pb.update(importcount)
        
        failed = []
        for f in files:
            try:
                submission_data, submissionform_data, documents = self._parse_doc(f)
                for key in submissionform_data:
                    data[key].append(submissionform_data[key])
                
            except Exception, e:
                failed.append(os.path.basename(f))
                failcount += 1
            finally:
                importcount += 1
                pb.update(importcount)

        sys.stderr.write('\n')
        if failed:
            
            self._warn('Failed to analyze %d files: %s' % (len(failed), ' '.join(failed)))
            sys.stderr.write('\n')
        
        
        def guess_type(values):
            number_count = str_count = decimal_count = 0
        
            for v in values:
                if re.match(r'\d+(\.\d+)?', v):
                    number_count += 1
                    if re.match(r'\d+\.\d+', v):
                        decimal_count += 1
                else:
                    str_count += 1
            
            if number_count > str_count and decimal_count:
                return 'DECIMAL'
            elif number_count > str_count and not decimal_count:
                return 'INTEGER'
            else:
                return 'STRING'
        
        fields = dict([(x.name, x.number,) for x in paper_forms.get_field_info_for_model(SubmissionForm) if x.number and x.name])
        
        not_imported_fields = []
        low_covered_fields = []
        for key in data:
            count = len(data[key])
            minimum = 0
            maximum = 0
            arithmetic_mean = 0
            geometric_mean = 0
            standard_deviation = 0
            optimum = 0
            guessed_type = 'NODATA'
            if not count == 0:
                lengths = [len(x) for x in data[key]]
                values = data[key]
                
                minimum = min(lengths)
                maximum = max(lengths)
                arithmetic_mean = mpf(sum(lengths))/count
                geometric_mean = mp.power(reduce(lambda x,y: x*y, lengths, 1), (mp.mpf(1)/count))
                standard_deviation = mp.sqrt(sum([mp.power(arithmetic_mean-x, 2) for x in lengths])/count)
                optimum = min(maximum, int(mp.ceil(arithmetic_mean+3*standard_deviation)))
                
                guessed_type = guess_type(values)
                
                if count < len(data) * 80 / 100:   # covering is lower than 80%
                    low_covered_fields.append('%s(%s)' % (fields[key], key))
                
            else:
                not_imported_fields.append('%s(%s)' % (fields[key], key))


            print '%s: count=%d minimum=%d maximum=%d arithmetic_mean=%.2f geometric_mean=%.2f standard_deviation=%.2f optimum=%d guessed_type=%s' % (key, count, minimum, maximum, arithmetic_mean, geometric_mean, standard_deviation, optimum, guessed_type)
            
        print '\n=== REPORT ==='
        print 'Not imported fields(%d): %s' % (len(not_imported_fields), ' '.join(not_imported_fields))
        print 'Low covered fields(%d): %s' % (len(low_covered_fields), ' '.join(low_covered_fields))
        

    def _import_file(self, filename):
        filename = os.path.expanduser(filename)
        if not os.path.isfile(filename):
            self._abort('"%s" does not exist' % filename)

        self._import_files([filename])

    def _import_dir(self, directory):
        path = os.path.expanduser(directory)
        if not os.path.isdir(path):
            self._abort('"%s" is not a directory' % path)

        files = [os.path.join(path, f) for f in os.listdir(path) if re.match('\d{1,4}_\d{4}(_.*)?.doc', f)]   # get all word documents in an existing directory
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
        antiword = _popen_antiword(filename)
        docbook, standard_error = antiword.communicate()
        if antiword.returncode:
            raise Exception(standard_error.strip())

        s = BeautifulSoup.BeautifulStoneSoup(docbook)
        x = s.findAll(text=re.compile("EK Nr."))
        y = [a.next.strip().split("/") for a in x]
        for q in y:
            q[0] = q[0].lstrip('0')
        documents = [os.path.join(os.path.dirname(filename), '%s_%s.doc' % (x[0], x[1])) for x in y]
        
        self._import_files(documents, dont_exit_on_fail=True)

        title = re.match('(.*).doc', os.path.basename(filename)).group(1)
        Meeting.objects.filter(title=title).delete()
        meeting = Meeting.objects.create(title=title, start=start)
        
        ec_numbers = ['%s%04d' % (a[1], int(a[0])) for a in y]
        submission_count = len(ec_numbers)
        fail_count = 0
        for ec_number in ec_numbers:
            #print "ec_number:",ec_number
            try:
                submission = Submission.objects.get(ec_number=ec_number)
                meeting.add_entry(submission=submission, duration_in_seconds=450)
            except Submission.DoesNotExist:
                fail_count += 1

        print '== %s/%s submissions assigned to meeting ==' % (submission_count-fail_count, submission_count)

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
            sys.stderr.write('\n'.join('%3d | %s' % (meeting.pk, meeting.title) for meeting in Meeting.objects.all()if not meeting.title.endswith('ohne Teilnehmer')))
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
        
        importcount = 0
        failcount = 0
        
        pb = ProgressBar(maximum=len(dataset))
        pb.update(importcount)
        
        failed_users = []
        failed_submissions = []
        failed_tentrys = []
            
        for (username, ec_numbers) in dataset:
            
            username = username.lower()
            try:
                sid = transaction.savepoint()
                user = User.objects.get(Q(username=username)|Q(username__startswith=username)|Q(username__endswith=username))
                
                for ec_number in ec_numbers:
                    try:
                        #ec_number = '%04d' % int(ec_number)
                        #ec_number = int(ec_number)
                        pass
                    except ValueError, e:
                        failed_submissions.append(ec_number)
                        continue
                    
                    try:
                        print "ec_number:",ec_number
                        rofl = transaction.savepoint()
                        t_entry = meeting.timetable_entries.get(submission__ec_number__endswith=ec_number)
                        Participation.objects.create(entry=t_entry, user=user)
                    except Exception, e:
                        transaction.savepoint_rollback(rofl)
                        failed_tentrys.append(ec_number)
                        continue
                    else:
                        transaction.savepoint_commit(rofl)

            except Exception, e:
                transaction.savepoint_rollback(sid)
                failed_users.append(username)
                failcount += 1
            else:
                transaction.savepoint_commit(sid)
            finally:
                importcount += 1
                pb.update(importcount)
        
        if failed_users:
            self._warn('\nCould not find users: %s\n' % (' '.join(failed_users)))
        if failed_tentrys:
            self._warn('\nCould not find timetable entries for submissions: %s\n' % (' '.join(unicode(s) for s in failed_tentrys)))
        if failed_submissions:
            self._warn('\nCould not find submissions: %s\n' % (' '.join(unicode(s) for s in failed_submissions)))
        
        
        print '== %d/%d participants imported ==' % (importcount - failcount, len(dataset))
        if failcount:
            self._abort('Failed to import %d participants' % failcount)
        else:
            print '\033[32mDone.\033[0m'

        sys.stdout.write('Splitting meeting... ')
        Meeting.objects.filter(title='%s ohne Teilnehmer' % (meeting.title)).delete()
        meeting_ohne = Meeting.objects.create(title='%s ohne Teilnehmer' % (meeting.title), start=meeting.start)
        for t_entry in meeting.timetable_entries.all():
            if not t_entry.participations.count():
                t_entry.meeting = meeting_ohne
                t_entry.save()
        sys.stdout.write('\033[32mdone\033[0m\n')


    @transaction.commit_on_success
    def _import_categorize(self, filename):
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
            sys.stderr.write('\n'.join('%3d | %s' % (meeting.pk, meeting.title) for meeting in Meeting.objects.all()if not meeting.title.endswith('ohne Teilnehmer')))
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
        
        importcount = 0
        failcount = 0
        
        pb = ProgressBar(maximum=len(dataset))
        pb.update(importcount)
        
        failed_abbrev = []
        failed_submissions = []
        
        for (medabbrev, ec_numbers) in dataset:
            try:
                sid = transaction.savepoint()
                medcat = MedicalCategory.objects.get(abbrev=medabbrev)
                
                for ec_number in ec_numbers:
                    
                    ec_number_parts = ec_number.split("/")
                    if len(ec_number_parts) > 1:
                        ec_number = '%s%04d' % (ec_number_parts[0], int(ec_number_parts[1].lstrip("0")))
                    #print "ec_number_new:",ec_number
                    try:
                        rofl = transaction.savepoint()
                        s = Submission.objects.get(ec_number=ec_number)
                        if not s.medical_categories.filter(abbrev=medabbrev):
                            s.medical_categories.add(medcat)
                            s.save()
                    except Exception, e:
                        transaction.savepoint_rollback(rofl)
                        failed_submissions.append(ec_number)
                        continue
                    else:
                        transaction.savepoint_commit(rofl)

            except Exception, e:
                transaction.savepoint_rollback(sid)
                failed_abbrev.append(medabbrev)
                failcount += 1
            else:
                transaction.savepoint_commit(sid)
            finally:
                importcount += 1
                pb.update(importcount)
        
        if failed_abbrev:
            self._warn('\nCould not find medical categories: %s\n' % (' '.join(failed_abbrev)))
        
        if failed_submissions:
            self._warn('\nCould not find submissions: %s\n' % (' '.join(failed_submissions)))

        print '== %d/%d categories imported ==' % (importcount - failcount, len(dataset))
        if failcount:
            self._abort('Failed to import %d participants' % failcount)
        else:
            print '\033[32mDone.\033[0m'

        sys.stdout.write('Splitting meeting... ')
        Meeting.objects.filter(title='%s ohne Teilnehmer' % (meeting.title)).delete()
        meeting_ohne = Meeting.objects.create(title='%s ohne Teilnehmer' % (meeting.title), start=meeting.start)
        for t_entry in meeting.timetable_entries.all():
            if not t_entry.submission.medical_categories.count():
                t_entry.meeting = meeting_ohne
                t_entry.save()
        sys.stdout.write('\033[32mdone\033[0m\n')

    @transaction.commit_on_success
    def _import_meeting_dates(self, filename):
        print "import_meeting_dates"
        from pprint import pprint
        
        parsed_dates = None
        
        try:
            #from deployment.utils import import_from
            #t = import_from(filename)
            #from parsed_dates import parsed_dates
            #cant import form src/deployment (import_from):
            import imp
            path, file = os.path.split(os.path.abspath(filename))
            name, ext = os.path.splitext(file)
            if not os.path.exists(filename):
                raise ImportError, name
            m = imp.load_source(name, filename)
            if not m:
                raise ImportError, name
            parsed_dates = m.parsed_dates
        except ImportError:
            self._abort('Failed to import %s' % filename)
            return None
        
        print "import module magic done, creating meetings"
        failed_meetings = 0
        imported_meetings = 0
        skipped_meetings = 0
        
        failed_deadlines = 0
        imported_deadlines = 0
        skipped_deadlines = 0
        
        failed_deadlines_diploma = 0
        imported_deadlines_diploma = 0
        skipped_deadlines_diploma = 0
        
        sp = transaction.savepoint()
        
        try:
            for mdates in parsed_dates:
                pdsp = transaction.savepoint()
                try:
                    mdate = mdates['meeting']
                    deadline_diplomathesis = mdates['deadline_diplomathesis']
                    deadline = mdates['deadline']
                    #deadline is "inclusive" .. i guess
                    if deadline.hour == 0:
                        deadline = deadline.replace(hour=23,minute=59)
                    if deadline_diplomathesis.hour == 0:
                        deadline_diplomathesis = deadline_diplomathesis.replace(hour=23,minute=59)
                    tmpm = Meeting.objects.filter(start__year=mdate.year,start__day=mdate.day,start__month=mdate.month)
                    if len(tmpm) > 0:
                        for m in tmpm:
                            #check if deadline fields are set for the already existing meetings 
                            if not m.deadline:
                                dsp = transaction.savepoint()
                                try:
                                    m.deadline = str(deadline)
                                    m.save()
                                except Exception, e:
                                    transaction.savepoint_rollback(dsp)
                                    failed_deadlines += 1
                                else:
                                    transaction.savepoint_commit(dsp)
                                    imported_deadlines += 1
                            else:
                                skipped_deadlines += 1
                            
                            if not m.deadline_diplomathesis:
                                dtsp = transaction.savepoint()
                                try:
                                    m.deadline_diplomathesis = str(deadline_diplomathesis)
                                    m.save()
                                except Exception, e:
                                    transaction.savepoint_rollback(dtsp)
                                    failed_deadlines_diploma += 1
                                else:
                                    transaction.savepoint_commit(dtsp)
                                    imported_deadlines_diploma += 1
                                    
                            else:
                                skipped_deadlines_diploma += 1
                        
                        skipped_meetings += 1
                        #temphack
                        #Meeting.objects.filter(start__year=mdate.year,start__day=mdate.day,start__month=mdate.month).delete()
                        
                    else:
                        #create meeting
                        #try:
                        title = "%s Meeting" % mdate.strftime("%b")
                        deadline_diplomathesis = mdates['deadline_diplomathesis']
                        deadline = mdates['deadline']
                        if mdate.hour == 0:
                            mdate = mdate.replace(hour=10)
                        
                        meeting = Meeting.objects.create(title=title, start=str(mdate), deadline=str(deadline), deadline_diplomathesis=str(deadline_diplomathesis))
                        print "created meeting %s, %s" % (meeting.title, meeting.start)
                        imported_meetings += 1
                        imported_deadlines += 1
                        imported_deadlines_diploma += 1
                except Exception, e:
                    transaction.savepoint_rollback(pdsp)
                    failed_meetings += 1
                else:
                    transaction.savepoint_commit(pdsp)
            
        except Exception, e:
            transaction.savepoint_rollback_sql(sp)
        else:
            transaction.savepoint_commit(sp)

        if skipped_deadlines > 0:
            print "skipped %d meeting deadlines" % skipped_deadlines
        if skipped_deadlines_diploma > 0:
            print "skipped %d meeting deadlines_diploma" % skipped_deadlines_diploma
        print "imported %d meeting deadlines" % imported_deadlines_diploma
        print "imported %d meeting deadlines_diploma" % imported_deadlines
        
        if failed_meetings > 0:
            print "failed to import %d meeting dates" % failed_meetings
        if skipped_meetings > 0:
            print "skipped %d meeting dates" % skipped_meetings
        print "imported %d meeting dates" % imported_meetings


    def handle(self, *args, **kwargs):
        options_count = sum([1 for x in [kwargs['submission_dir'], kwargs['submission'], kwargs['timetable'], kwargs['categorize'], kwargs['participants'], kwargs['analyze_dir'], kwargs['meeting_dates']] if x])
        if options_count is not 1:
            self._abort('please specifiy one of -d/-s/-t/-c/-p/-a')

        if kwargs['submission_dir']:
            self._import_dir(kwargs['submission_dir'])
        elif kwargs['submission']:
            self._import_file(kwargs['submission'])
        elif kwargs['timetable']:
            self._import_timetable(kwargs['timetable'], kwargs['date'])
        elif kwargs['participants']:
            self._import_participants(kwargs['participants'])
        elif kwargs['categorize']:
            self._import_categorize(kwargs['categorize'])
        elif kwargs['analyze_dir']:
            self._analyze_dir(kwargs['analyze_dir'])
        elif kwargs['meeting_dates']:
            self._import_meeting_dates(kwargs['meeting_dates'])
        sys.exit(0)


