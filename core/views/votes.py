import datetime
import os
import tempfile
import urllib
import urllib2

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from ecs.core.views.utils import render, render_pdf, pdf_response
from ecs.core.models import Meeting, TimetableEntry, Submission, Vote, Document
from ecs.core.forms.meetings import MeetingForm, SubmissionSchedulingForm
from ecs.core.forms.voting import VoteForm, SaveVoteForm
from ecs.pdfsigner.views import get_random_id, id_set, id_get, id_delete, sign

from ecs.utils import forceauth
from ecs.utils.pdfutils import xhtml2pdf


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
