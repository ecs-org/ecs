import datetime
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.contrib.auth.models import User
from django.utils.datastructures import SortedDict
from django.db.models import Count
from ecs.core.views.utils import render, render_html, render_pdf, pdf_response
from ecs.core.models import Meeting, Participation, TimetableEntry, Submission, MedicalCategory, Participation, Vote, ChecklistBlueprint
from ecs.core.forms.meetings import MeetingForm, TimetableEntryForm, FreeTimetableEntryForm, UserConstraintFormSet, SubmissionSchedulingForm
from ecs.core.forms.voting import VoteForm, SaveVoteForm
from ecs.core.task_queue import optimize_timetable_task
from ecs.utils.timedelta import parse_timedelta

from ecs.messages.mail import send_mail
from ecs.ecsmail.persil import whitewash


import datetime
import os
import tempfile
import urllib
import urllib2

from django.http import HttpResponseForbidden

from ecs.core.models import Document
from ecs.pdfsigner.views import get_random_id, id_set, id_get, id_delete, sign
from ecs.utils import forceauth
from ecs.utils.xhtml2pdf import xhtml2pdf


def create_meeting(request):
    form = MeetingForm(request.POST or None)
    if form.is_valid():
        meeting = form.save()
        return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    return render(request, 'meetings/form.html', {
        'form': form,
    })
    
def meeting_list(request):
    return render(request, 'meetings/list.html', {
        #.filter(start__gte=datetime.datetime.now())
        'meetings': Meeting.objects.order_by('start')
    })
    
def schedule_submission(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    form = SubmissionSchedulingForm(request.POST or None)
    if form.is_valid():
        kwargs = form.cleaned_data.copy()
        meeting = kwargs.pop('meeting')
        timetable_entry = meeting.add_entry(submission=submission, duration=datetime.timedelta(minutes=7.5), **kwargs)
        return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    return render(request, 'submissions/schedule.html', {
        'submission': submission,
        'form': form,
    })
    
def add_free_timetable_entry(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    form = FreeTimetableEntryForm(request.POST or None)
    if form.is_valid():
        entry = meeting.add_entry(**form.cleaned_data)
        return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    return render(request, 'meetings/timetable/add_free_entry.html', {
        'form': form,
        'meeting': meeting,
    })
    

def add_timetable_entry(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    is_break = request.GET.get('break', False)
    if is_break:
        entry = meeting.add_break(duration=datetime.timedelta(minutes=30))
    else:
        entry = meeting.add_entry(duration=datetime.timedelta(minutes=7, seconds=30), submission=Submission.objects.order_by('?')[:1].get())
        import random
        for user in User.objects.order_by('?')[:random.randint(1, 4)]:
            Participation.objects.create(entry=entry, user=user)
    return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    
def remove_timetable_entry(request, meeting_pk=None, entry_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    entry = get_object_or_404(TimetableEntry, pk=entry_pk)
    entry.delete()
    return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    
def update_timetable_entry(request, meeting_pk=None, entry_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    entry = get_object_or_404(TimetableEntry, pk=entry_pk)
    form = TimetableEntryForm(request.POST)
    if form.is_valid():
        entry.duration = form.cleaned_data['duration']
        entry.optimal_start = form.cleaned_data['optimal_start']
        entry.save()
    return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    
def move_timetable_entry(request, meeting_pk=None):
    from_index = int(request.GET.get('from_index'))
    to_index = int(request.GET.get('to_index'))
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    meeting[from_index].index = to_index
    return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    
def users_by_medical_category(request):
    category = get_object_or_404(MedicalCategory, pk=request.POST.get('category'))
    users = list(User.objects.filter(medical_categories=category, ecs_profile__board_member=True).values('pk', 'username'))
    return HttpResponse(simplejson.dumps(users), content_type='text/json')

def timetable_editor(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    return render(request, 'meetings/timetable/editor.html', {
        'meeting': meeting,
        'running_optimization': bool(meeting.optimization_task_id),
    })
    
def participation_editor(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    users = User.objects.all()
    entries = meeting.timetable_entries.exclude(submission=None).select_related('submission')
    if request.method == 'POST':
        for entry in entries:
            for cat in entry.medical_categories:
                participations = Participation.objects.filter(entry=entry, medical_category=cat)
                user_pks = set(map(int, request.POST.getlist('users_%s_%s' % (entry.pk, cat.pk))))
                participations.exclude(user__pk__in=user_pks).delete()
                for user in User.objects.filter(pk__in=user_pks).exclude(meeting_participations__in=participations.values('pk')):
                    entry.add_user(user, cat)
            
    return render(request, 'meetings/timetable/participation_editor.html', {
        'meeting': meeting,
        'categories': MedicalCategory.objects.all(),
    })

def medical_categories(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)

    return render(request, 'meetings/timetable/medical_categories.html', {
        'meeting': meeting,    
    })

def optimize_timetable(request, meeting_pk=None, algorithm=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not meeting.optimization_task_id:
        retval = optimize_timetable_task.delay(meeting_id=meeting.id,algorithm=algorithm)
        meeting.optimization_task_id = retval.task_id
        meeting.save()
    return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))

def edit_user_constraints(request, meeting_pk=None, user_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    user = get_object_or_404(User, pk=user_pk)
    constraint_formset = UserConstraintFormSet(request.POST or None, prefix='constraint', queryset=user.meeting_constraints.all())
    if constraint_formset.is_valid():
        for constraint in constraint_formset.save(commit=False):
            constraint.meeting = meeting
            constraint.user = user
            constraint.save()
        return HttpResponseRedirect(reverse('ecs.core.views.meetings.edit_user_constraints', kwargs={'meeting_pk': meeting.pk, 'user_pk': user.pk}))
    return render(request, 'meetings/constraints/user_form.html', {
        'meeting': meeting,
        'participant': user,
        'constraint_formset': constraint_formset,
    })
    
def meeting_assistant_quickjump(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, started__isnull=False)
    top = None
    q = request.REQUEST.get('q', '').upper()
    explict_top = 'TOP' in q
    q = q.replace('TOP', '').strip()
    
    # if we don't explicitly look for a TOP, try an exact ec_number lookup
    if not explict_top:
        tops = meeting.timetable_entries.filter(submission__ec_number__iexact=q).order_by('timetable_index')
        if len(tops) == 1:
            top = tops[0]
    # if we found no TOP yet, try an exact TOP index lookup
    if not top:
        try:
            top = meeting.timetable_entries.get(timetable_index=int(q)-1)
        except (ValueError, TimetableEntry.DoesNotExist):
            pass
    # if we found no TOP yet and don't explicitly look for a TOP, try a fuzzy ec_number lookup
    if not top and not explict_top:
        tops = meeting.timetable_entries.filter(submission__ec_number__icontains=q).order_by('timetable_index')
        if len(tops) == 1:
            top = tops[0]
    if top:
        return HttpResponseRedirect(reverse('ecs.core.views.meeting_assistant_top', kwargs={'meeting_pk': meeting.pk, 'top_pk': top.pk}))
    
    return render(request, 'meetings/assistant/quickjump_error.html', {
        'meeting': meeting,
        'tops': tops,
    })
    
def meeting_assistant(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if meeting.started:
        if meeting.ended:
            return render(request, 'meetings/assistant/error.html', {
                'meeting': meeting,
                'message': 'Diese Sitzung wurde beendet.',
            })
        try:
            top_pk = request.session.get('meetings:%s:assistant:top_pk' % meeting.pk, None) or meeting[0].pk
            return HttpResponseRedirect(reverse('ecs.core.views.meeting_assistant_top', kwargs={'meeting_pk': meeting.pk, 'top_pk': top_pk}))
        except IndexError:
            return render(request, 'meetings/assistant/error.html', {
                'meeting': meeting,
                'message': 'Dieser Sitzung sind keine TOPs zugeordnet.',
            })
    else:
        return render(request, 'meetings/assistant/error.html', {
            'meeting': meeting,
            'message': 'Dieses Sitzung wurde noch nicht begonnen.',
        })
        
def meeting_assistant_start(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, started=None)
    meeting.started = datetime.datetime.now()
    meeting.save()
    return HttpResponseRedirect(reverse('ecs.core.views.meeting_assistant', kwargs={'meeting_pk': meeting.pk}))
    
def meeting_assistant_stop(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, started__isnull=False)
    if meeting.open_tops.count():
        raise Http404("unfinished meetings cannot be stopped")
    meeting.ended = datetime.datetime.now()
    meeting.save()
    return HttpResponseRedirect(reverse('ecs.core.views.meeting_assistant', kwargs={'meeting_pk': meeting.pk}))

def meeting_assistant_top(request, meeting_pk=None, top_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk, started__isnull=False)
    top = get_object_or_404(TimetableEntry, pk=top_pk)
    simple_save = request.POST.get('simple_save', False)
    autosave = request.POST.get('autosave', False)
    vote, form = None, None
    
    def next_top_redirect():
        if top.next_open:
            next_top = top.next_open
        else:
            try:
                next_top = meeting.open_tops[0]
            except IndexError:
                return HttpResponseRedirect(reverse('ecs.core.views.meeting_assistant', kwargs={'meeting_pk': meeting.pk}))
        return HttpResponseRedirect(reverse('ecs.core.views.meeting_assistant_top', kwargs={'meeting_pk': meeting.pk, 'top_pk': next_top.pk}))
    
    if top.submission:
        try:
            vote = top.vote
        except Vote.DoesNotExist:
            pass
        if simple_save:
            form_cls = SaveVoteForm
        else:
            form_cls = VoteForm
        form = form_cls(request.POST or None, instance=vote)
        if form.is_valid():
            vote = form.save(commit=False)
            vote.top = top
            vote.save()
            if autosave:
                return HttpResponse('OK')
            if form.cleaned_data['close_top']:
                top.is_open = False
                top.save()
            return next_top_redirect()
    elif request.method == 'POST':
        top.is_open = False
        top.save()
        return next_top_redirect()

    last_top_cache_key = 'meetings:%s:assistant:top_pk' % meeting.pk
    last_top = None
    if last_top_cache_key in request.session:
        last_top = TimetableEntry.objects.get(pk=request.session[last_top_cache_key])
    request.session[last_top_cache_key] = top.pk
    
    checklist_review_states = SortedDict()
    if top.submission:
        for blueprint in ChecklistBlueprint.objects.order_by('name'):
            checklist_review_states[blueprint] = None
        for checklist in top.submission.checklists.select_related('blueprint'):
            checklist_review_states[checklist.blueprint] = checklist

    return render(request, 'meetings/assistant/top.html', {
        'meeting': meeting,
        'submission': top.submission,
        'top': top,
        'vote': vote,
        'form': form,
        'last_top': last_top,
        'checklist_review_states': checklist_review_states.items(),
    })

def meeting_assistant_clear(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    Vote.objects.filter(top__meeting=meeting).delete()
    meeting.timetable_entries.update(is_open=True)
    meeting.started = None
    meeting.ended = None
    meeting.save()
    return HttpResponseRedirect(reverse('ecs.core.views.meeting_assistant', kwargs={'meeting_pk': meeting.pk}))


def agenda_pdf(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    filename = '%s-%s-Agenda.pdf' % (
        meeting.title, meeting.start.strftime('%d-%m-%Y')
    )
    
    pdf = render_pdf(request, 'db/meetings/xhtml2pdf/agenda.html', {
        'meeting': meeting,
    })
    return pdf_response(pdf, filename=filename)

def timetable_pdf(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    
    timetable = {}
    for entry in meeting:
        for user in entry.users:
            if user in timetable:
                timetable[user].append(entry)
            else:
                timetable[user] = [entry]
    
    timetable = sorted([{
        'user': key,
        'entries': sorted(timetable[key], key=lambda x:x.timetable_index),
    } for key in timetable], key=lambda x:x['user'])
    
    for row in timetable:
        first_entry = row['entries'][0]
        times = [{'start': first_entry.start, 'end': first_entry.end, 'index': first_entry.timetable_index}]
        for entry in row['entries'][1:]:
            if times[-1]['end'] == entry.start:
                times[-1]['end'] = entry.end
            else:
                times.append({'start': entry.start, 'end': entry.end, 'index': entry.timetable_index})
    
        row['times'] = ', '.join(['%s - %s' % (x['start'].strftime('%H:%M'), x['end'].strftime('%H:%M')) for x in times])
    
    filename = '%s-%s-Zeitfenster.pdf' % (
        meeting.title, meeting.start.strftime('%d-%m-%Y')
    )
    
    pdf = render_pdf(request, 'db/meetings/xhtml2pdf/timetable.html', {
        'meeting': meeting,
        'timetable': timetable,
    })
    return pdf_response(pdf, filename=filename)

def agenda_htmlemail(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    filename = '%s-%s-Agenda.pdf' % (
        meeting.title, meeting.start.strftime('%d-%m-%Y')
    )
    pdf = render_pdf(request, 'db/meetings/xhtml2pdf/agenda.html', {
        'meeting': meeting,
    })

    for recipient in settings.AGENDA_RECIPIENT_LIST:        
        htmlmail = unicode(render_html(request, 'meetings/email/invitation-with-agenda.html', {
            'meeting': meeting,
            'recipient': recipient,
        }))
        plainmail = whitewash(htmlmail)

        # FIXME: this should go into a celery queue and not be called directly
        send_mail(subject='Invitation to meeting', 
                 message=plainmail,
                 message_html=htmlmail,
                 attachments=[(filename, pdf,'application/pdf'),],
                 from_email=settings.DEFAULT_FROM_EMAIL,
                 recipient_list=settings.AGENDA_RECIPIENT_LIST, fail_silently=False)
        
    return HttpResponseRedirect(reverse('ecs.core.views.meeting_list'))

def timetable_htmlemailpart(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    response = render(request, 'meetings/email/timetable.html', {
        'meeting': meeting,
    })
    return response


#
#  votes signing
#

def votes_signing(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    tops = meeting.timetable_entries.all()
    votes_list = [ ]
    for top in tops:
        votes = Vote.objects.filter(top=top)
        c = votes.count()
        assert(c < 2)
        if c is 0:
            vote = None
        else:
            vote = votes[0]
        votes_list.append({'top_index': top.index, 'top': str(top), 'vote': vote})
    response = render(request, 'meetings/votes_signing.html', {
        'meeting': meeting,
        'votes_list': votes_list,
    })
    return response


def vote_filename(meeting, vote):
    vote_name = vote.get_ec_number()
    if vote_name is None:
        vote_name = 'id_%s' % vote.pk
    top = str(vote.top)
    filename = '%s-%s-%s-Vote_%s.pdf' % (meeting.title, meeting.start.strftime('%d-%m-%Y'), top, vote_name)
    return filename.replace(' ', '_')


def vote_context(meeting, vote):
    top = vote.top
    submission = None
    form = None
    documents = None
    if top:
        submission = top.submission
    if submission and submission.forms.count() > 0:
        form = submission.forms.all()[0]
    if form:
        documents = form.documents.all()
    vote_date = meeting.start.strftime('%d.%m.%Y')
    ec_number = str(vote.get_ec_number())
    context = {
        'meeting': meeting,
        'vote': vote,
        'submission': submission,
        'form': form,
        'documents': documents,
        'vote_date': vote_date,
        'ec_number': ec_number,
    }
    return context


def vote_pdf(request, meeting_pk=None, vote_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    vote = get_object_or_404(Vote, pk=vote_pk)
    pdf_name = vote_filename(meeting, vote)
    template = 'db/meetings/xhtml2pdf/vote.html'
    context = vote_context(meeting, vote)
    pdf = render_pdf(request, template, context)
    # TODO get uuid
    # TODO stamp with barcode(uuid)
    return pdf_response(pdf, filename=pdf_name)


def vote_sign(request, meeting_pk=None, vote_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    vote = get_object_or_404(Vote, pk=vote_pk)
    print 'vote_sign meeting "%s", vote "%s"' % (meeting_pk, vote_pk)
    pdf_name = vote_filename(meeting, vote)
    template = 'db/meetings/xhtml2pdf/vote.html'
    context = vote_context(meeting, vote)
    html = render(request, template, context).content
    pdf = xhtml2pdf(html)
    pdf_len = len(pdf)
    pdf_id = get_random_id()
    t = tempfile.NamedTemporaryFile(prefix='vote_sign_', suffix='.pdf', delete=False)
    t_name = t.name
    t.write(pdf)
    t.close()
    id_set(pdf_id, 'vote sign:%s:%s' % (t_name, pdf_name))
    return sign(request, pdf_id, pdf_len, pdf_name)


@forceauth.exempt
def vote_sign_send(request, meeting_pk=None, vote_pk=None):
    print 'vote_sign_send meeting "%s", vote "%s"' % (meeting_pk, vote_pk)
    if request.REQUEST.has_key('pdf-id'):
        pdf_id = request.REQUEST['pdf-id']
    else:
        return HttpResponseForbidden('<h1>Error: Missing pdf-id</h1>')
    value = id_get(pdf_id)
    if value is None:
        return HttpResponseForbidden('<h1>Error: Invalid pdf-id</h1>')
    a = value.split(':')
    t_name = a[1]
    pdf_data = file(t_name, 'rb')
    return HttpResponse(pdf_data, mimetype='application/pdf')


@forceauth.exempt
def vote_sign_receive(request, meeting_pk=None, vote_pk=None, jsessionid=None):
    print 'vote_sign_receive meeting "%s", vote "%s", jsessionid "%s"' % (meeting_pk, vote_pk, jsessionid)
    if request.REQUEST.has_key('pdf-url') and request.REQUEST.has_key('pdf-id') and request.REQUEST.has_key('num-bytes') and request.REQUEST.has_key('pdfas-session-id'):
       pdf_url = request.REQUEST['pdf-url']
       pdf_id = request.REQUEST['pdf-id']
       num_bytes = request.REQUEST['num-bytes']
       pdfas_session_id = request.REQUEST['pdfas-session-id']
       url = '%s%s?pdf-id=%s&num-bytes=%s&pdfas-session-id=%s' % (settings.PDFAS_SERVICE, pdf_url, pdf_id, num_bytes, pdfas_session_id)
       value = id_get(pdf_id)
       if value is None:
           return HttpResponseForbidden('<h1>Error: Invalid pdf-id</h1>')
       a = value.split(':')
       t_name = a[1]
       pdf_name = a[2]
       os.remove(t_name)
       id_delete(pdf_id)
       # f is not seekable, so we have to store it as local file first
       f = urllib2.urlopen(url)
       t = tempfile.NamedTemporaryFile(prefix='vote_sign_', suffix='.pdf', delete=False)
       t_name = t.name
       t.write(f.read())
       t.close()
       f.close()
       print 'wrote "%s" as "%s"' % (pdf_name, t_name)
       t = open(t_name, 'rb')
       d = datetime.datetime.now()
       # TODO prevent barcode stamping (don't touch the signed pdf!)
       document = Document(file=t, original_file_name=pdf_name, date=d)
       document.save()
       print 'stored "%s" as "%s"' % (pdf_name, document.pk)
       t.close()
       os.remove(t_name)
       return HttpResponseRedirect(reverse('ecs.pdfviewer.views.show', kwargs={'id': document.pk, 'page': 1, 'zoom': '1'}))
    return HttpResponse('vote_sign__receive: got [%s]' % request)


def vote_sign_error(request, meeting_pk=None, vote_pk=None):
    if request.REQUEST.has_key('error'):
        error = urllib.unquote_plus(request.REQUEST['error'])
    else:
        error = ''
    if request.REQUEST.has_key('cause'):
        cause = urllib.unquote_plus(request.REQUEST['cause'])  # FIXME can't deal with UTF-8 encoded Umlauts
    else:
        cause = ''
    # no pdf id, no explicit cleaning possible
    return HttpResponse('<h1>vote_sign_error: error=[%s], cause=[%s]</h1>' % (error, cause))
