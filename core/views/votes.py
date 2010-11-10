import datetime
import os
import tempfile
import urllib
import urllib2

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from ecs.utils.viewutils import render, render_pdf, pdf_response
from ecs.core.models import Vote
from ecs.meetings.models import Meeting
from ecs.documents.models import Document, DocumentType
from ecs.pdfsigner.views import sign

from ecs.utils import forceauth
from ecs.utils.pdfutils import xhtml2pdf, pdf_barcodestamp
from django.core.files.base import File
from django.views.decorators.csrf import csrf_exempt
from uuid import uuid4
from ecs.pdfsigner.UnsignedVoteDepot import UnsignedVoteDepot

votesDepot = UnsignedVoteDepot();

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
    document_uuid = uuid4();
    html = render(request, template, context).content
    pdf = xhtml2pdf(html)
    pdf_len = len(pdf)

    t = tempfile.NamedTemporaryFile(prefix='vote_sign_', suffix='.pdf', delete=False)
    pdf_barcodestamp(pdf, t, document_uuid)
    t.close()

    pdf_id = votesDepot.deposit(t, pdf_name)
    return sign(request, pdf_id, pdf_len, pdf_name)


@forceauth.exempt
def vote_sign_send(request, meeting_pk=None, vote_pk=None):
    print 'vote_sign_send meeting "%s", vote "%s"' % (meeting_pk, vote_pk)
    if request.REQUEST.has_key('pdf-id'):
        pdf_id = request.REQUEST['pdf-id']
    else:
        return HttpResponseForbidden('<h1>Error: Missing pdf-id</h1>')
    pdf_file, display_name = votesDepot.pickup(pdf_id)
    if pdf_file is None:
        return HttpResponseForbidden('<h1>Error: Invalid pdf-id</h1>')

    return HttpResponse(pdf_file, mimetype='application/pdf')

@csrf_exempt
def vote_sign_receive_landing(request, meeting_pk=None, vote_pk=None, jsessionid=None):
    return vote_sign_receive(request, meeting_pk, vote_pk, jsessionid);
 
@forceauth.exempt
def vote_sign_receive(request, meeting_pk=None, vote_pk=None, jsessionid=None):
    print 'vote_sign_receive meeting "%s", vote "%s", jsessionid "%s"' % (meeting_pk, vote_pk, jsessionid)
    if request.REQUEST.has_key('pdf-url') and request.REQUEST.has_key('pdf-id') and request.REQUEST.has_key('num-bytes') and request.REQUEST.has_key('pdfas-session-id'):
        pdf_url = request.REQUEST['pdf-url']
        pdf_id = request.REQUEST['pdf-id']
        num_bytes = int(request.REQUEST['num-bytes'])
        pdfas_session_id = request.REQUEST['pdfas-session-id']
        url = '%s%s?pdf-id=%s&num-bytes=%s&pdfas-session-id=%s' % (settings.PDFAS_SERVICE, pdf_url, pdf_id, num_bytes, pdfas_session_id)
        pdf_file, display_name = votesDepot.pickup(pdf_id)
        if pdf_file is None:
            return HttpResponseForbidden('<h1>Error: Invalid pdf-id</h1>')

        # f_pdfas is not seekable, so we have to store it as local file first
        sock_pdfas = urllib2.urlopen(url)
        t_pdfas = tempfile.NamedTemporaryFile(prefix='vote_sign_', suffix='.pdf', delete=False)
        t_pdfas.write(sock_pdfas.read(num_bytes))
        t_pdfas.close()
        sock_pdfas.close()

        print 'wrote "%s" as "%s"' % (display_name, t_pdfas.name)

        d = datetime.datetime.now()
        doctype = DocumentType.objects.create(name="Votum", identifier="votes")
        document = Document.objects.create(document_uuid=pdf_id, doctype=doctype, file=File(pdf_file), original_file_name=display_name, date=d)
        pdf_file.close()

        print 'stored "%s" as "%s"' % (display_name, document.pk)
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