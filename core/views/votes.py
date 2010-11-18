import datetime
import os
import tempfile
import urllib
import urllib2

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse,\
    Http404
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from ecs.utils.viewutils import render, render_pdf, pdf_response
from ecs.core.models import Vote
from ecs.meetings.models import Meeting
from ecs.documents.models import Document, DocumentType

from ecs.utils import forceauth
from ecs.utils.pdfutils import xhtml2pdf, pdf_barcodestamp
from django.core.files.base import File
from django.views.decorators.csrf import csrf_exempt
from ecs.utils.votedepot import VoteDepot
from uuid import uuid4

votesDepot = VoteDepot();

def vote_show(request, meeting_pk=None, vote_pk=None):
    vote = get_object_or_404(Vote, pk=vote_pk)
    return render(request, 'db/meetings/xhtml2pdf/vote.html', vote_context(vote))

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


def vote_filename(vote):
    meeting = vote.top.meeting;
    vote_name = vote.get_ec_number()
    
    if vote_name is None:
        vote_name = 'id_%s' % vote.pk
    top = str(vote.top)
    filename = '%s-%s-%s-Vote_%s.pdf' % (meeting.title, meeting.start.strftime('%d-%m-%Y'), top, vote_name)
    return filename.replace(' ', '_')


def vote_context(vote):
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
    vote_date = top.meeting.start.strftime('%d.%m.%Y')
    
    context = {
        'meeting': top.meeting,
        'vote': vote,
        'submission': submission,
        'form': form,
        'documents': documents,
        'vote_date': vote_date,
        'ec_number': submission.get_ec_number_display(),
    }
    return context


def vote_pdf(request, meeting_pk=None, vote_pk=None):
    vote = get_object_or_404(Vote, pk=vote_pk)
    pdf_name = vote_filename(vote)
    pdf_template = 'db/meetings/xhtml2pdf/vote.html'
    context = vote_context(vote)
    pdf = render_pdf(request, pdf_template, context)
    return pdf_response(pdf, filename=pdf_name)

def vote_sign(request, meeting_pk=None, vote_pk=None):
    vote = get_object_or_404(Vote, pk=vote_pk)
    print 'vote_sign vote "%s"' % (vote_pk)
    pdf_name = vote_filename(vote)
    pdf_template = 'db/meetings/xhtml2pdf/vote.html'
    preview_template = 'db/meetings/xhtml2pdf/vote_preview.html'
    
    context = vote_context(vote)
    html_preview = render(request, preview_template, context).content
    pdf_data = xhtml2pdf(render(request, pdf_template, context).content)
    document_uuid = uuid4().get_hex();

    t_in = tempfile.NamedTemporaryFile(prefix='vote_sign_', suffix='.pdf', delete=False)
    t_out = tempfile.NamedTemporaryFile(prefix='vote_sign_stamped_', suffix='.pdf', delete=False)
    t_in.write(pdf_data)

    t_in.seek(0)
    pdf_barcodestamp(t_in, t_out, document_uuid)
    t_in.close();

    t_out.seek(0)
    pdf_data_stamped = t_out.read()
    t_out.close();
    
    pdfas_id = votesDepot.deposit(pdf_data_stamped, html_preview, document_uuid, pdf_name)
    return sign(request, pdfas_id, len(pdf_data_stamped), pdf_name)


@forceauth.exempt
def vote_sign_send(request, meeting_pk=None, vote_pk=None):
    votedoc = votesDepot.get(request.REQUEST['pdf-id'])
    if votedoc is None:
        return HttpResponseForbidden('<h1>Error: Invalid pdf-id. Probably your signing session expired. Please retry.</h1>')

    t_pdfas = tempfile.NamedTemporaryFile(prefix='bla', suffix='.pdf', delete=False)
    t_pdfas.write(votedoc["pdf_data"])
    t_pdfas.seek(0)
    
    return HttpResponse(t_pdfas.read(), mimetype='application/pdf')

@forceauth.exempt
@csrf_exempt
def vote_sign_preview(request, meeting_pk=None, vote_pk=None, jsessionid=None):
    votedoc = votesDepot.get(request.REQUEST['pdf-id'])
    if votedoc is None:
        return HttpResponseForbidden('<h1>Error: Invalid pdf-id. Probably your signing session expired. Please retry.</h1>')
    
    return HttpResponse(votedoc["html_preview"])

@csrf_exempt
def vote_sign_receive_landing(request,  meeting_pk=None, vote_pk=None, jsessionid=None):
    return vote_sign_receive(request, vote_pk, jsessionid);
 
@forceauth.exempt
def vote_sign_receive(request, meeting_pk=None, vote_pk=None, jsessionid=None):
    print 'vote_sign_receive vote "%s"' % (vote_pk)
    vote = get_object_or_404(Vote, pk=vote_pk)
    
    if request.REQUEST.has_key('pdf-url') and request.REQUEST.has_key('pdf-id') and request.REQUEST.has_key('num-bytes') and request.REQUEST.has_key('pdfas-session-id'):
        pdf_url = request.REQUEST['pdf-url']
        pdf_id = request.REQUEST['pdf-id']
        num_bytes = int(request.REQUEST['num-bytes'])
        pdfas_session_id = request.REQUEST['pdfas-session-id']
        url = '%s%s?pdf-id=%s&num-bytes=%s&pdfas-session-id=%s' % (settings.PDFAS_SERVICE, pdf_url, pdf_id, num_bytes, pdfas_session_id)
        votedoc = votesDepot.pop(pdf_id)
        if votedoc is None:
            return HttpResponseForbidden('<h1>Error: Invalid pdf-id. Probably your signing session expired. Please retry.</h1>')

        # f_pdfas is not seekable, so we have to store it as local file first
        sock_pdfas = urllib2.urlopen(url)
        t_pdfas = tempfile.NamedTemporaryFile(prefix='vote_sign_', suffix='.pdf', delete=False)
        t_pdfas.write(sock_pdfas.read(num_bytes))
        sock_pdfas.close()
         
        d = datetime.datetime.now()
        doctype = DocumentType.objects.create(name="Votum", identifier="votes")
        document = Document.objects.create(uuid_document=votedoc["uuid"], parent_object=vote, branding='n', doctype=doctype, file=File(t_pdfas), original_file_name=votedoc["name"], date=d)
        t_pdfas.close()
        os.remove(t_pdfas.name)
        
        return HttpResponseRedirect(reverse('ecs.pdfviewer.views.show', kwargs={'document_pk': document.pk}))
    return HttpResponse('vote_sign__receive: got [%s]' % request)

def download_signed_vote(request, meeting_pk=None, vote_pk=None):
    vote = get_object_or_404(Vote, pk=vote_pk)
    
    if vote.signed_at is None:
        raise Http404('Vote has not been signed yet: %s' % (vote_pk))
        
    signed_vote_doc = Document.objects.get(parent_object=vote)
    if signed_vote_doc is None:
        raise Http404('No signed document for vote %s available' % (vote_pk))
    
    return pdf_response(signed_vote_doc.file.read(), filename=signed_vote_doc.original_file_name)

@csrf_exempt
def vote_sign_error(request, meeting_pk=None, vote_pk=None):
    if request.REQUEST.has_key('pdf-id'):
        votesDepot.pop(request.REQUEST['pdf-id'])
        
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

def sign(request, pdf_id, pdf_data_size, pdf_name):
    url_sign = '%sSign' % settings.PDFAS_SERVICE
    url_send = request.build_absolute_uri('send')
    url_error = request.build_absolute_uri('error')
    url_receive = request.build_absolute_uri('receive')
    url_preview = request.build_absolute_uri('preview')
    print 'url_sign: "%s"' % url_sign
    print 'url_send: "%s"' % url_send
    print 'url_error: "%s"' % url_error
    print 'url_receive: "%s"' % url_receive
    values = {
        'preview': 'false',
        'connector': 'moc',  # undocumented feature! selects ONLINE CCE/BKU
        'mode': 'binary',
        'sig_type': 'SIGNATURBLOCK_DE',
        'inline': 'false',
        'filename': pdf_name,
        'num-bytes': '%s' % pdf_data_size,
        'pdf-url': url_send,
        'pdf-id': pdf_id,
        'invoke-app-url': url_receive, 
        'invoke-app-error-url': url_error,
        'invoke-preview-url': url_preview,
        # session-id=9085B85B364BEC31E7D38047FE54577D
        'locale': 'de',
    }
    data = urllib.urlencode(values)
    redirect = '%s?%s' % (url_sign, data)
    print 'sign: redirect to [%s]' % redirect
    return HttpResponseRedirect(redirect)

