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

from ecs.utils import forceauth
from ecs.utils.pdfutils import xhtml2pdf
from django.core.files.base import File
from django.views.decorators.csrf import csrf_exempt
from ecs.utils.votedepot import VoteDepot

'''
@startuml img/sequence_img001.png
Actor Alice #orange
participant Ecs #lightgreen
participant PDFas #pink
participant Applet #yellow

Alice -> Ecs: View available votes

activate Ecs #orange
    Alice -> Ecs: Request signing of a vote
    Ecs -> PDFas: Bump start signing,\nimpart unsigned vote download url 
    activate PDFas #lightgreen
        activate Ecs #pink
            Ecs -> Alice: Redirect to signing applet
            PDFas -> Ecs : Download unsigned vote
            Alice -> Applet: Provide security token 
            activate Applet #orange
                Applet -> PDFas: Autenticate,\ndeliver security token
                activate PDFas #yellow
                    PDFas -> Ecs : Bump signed vote ready,\nimpart signed vote download url
                    PDFas -> Applet: Notify success
                deactivate Applet #orange
            deactivate PDFas #yellow
            Ecs -> PDFas : Download signed vote
        deactivate PDFas #lightgreen
    deactivate Ecs #pink
    Ecs -> Alice : Redirect to show vote view
    Alice -> Ecs: View signed vote
deactivate Ecs #orange

@enduml
'''

votesDepot = VoteDepot();

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
    pdf_data = xhtml2pdf(html)
    pdf_len = len(pdf_data)

    pdf_id = votesDepot.deposit(pdf_data, pdf_name)
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
        os.remove(pdf_file)
        
        print 'stored "%s" as "%s"' % (display_name, document.pk)
        return HttpResponseRedirect(reverse('ecs.pdfviewer.views.show', kwargs={'id': document.pk, 'page': 1, 'zoom': '1'}))
    return HttpResponse('vote_sign__receive: got [%s]' % request)

def vote_sign_error(request, meeting_pk=None, vote_pk=None):
    if request.REQUEST.has_key('pdf-id'):
        pdf_file, display_name = votesDepot.pickup(request.REQUEST['pdf-id'])
        pdf_file.close();
        os.remove(pdf_file)
        
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

# TODO BKUApplet - setting background from 
# http://ecsdev.ep3.at:4780/bkuonline/img/chip32.png
# to something ECS branded

def sign(request, pdf_id, pdf_data_size, pdf_name):
    url_sign = '%sSign' % settings.PDFAS_SERVICE
    url_send = request.build_absolute_uri('send')
    url_error = request.build_absolute_uri('error')
    url_receive = request.build_absolute_uri('receive')
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
        # session-id=9085B85B364BEC31E7D38047FE54577D
        'locale': 'de',
    }
    data = urllib.urlencode(values)
    redirect = '%s?%s' % (url_sign, data)
    print 'sign: redirect to [%s]' % redirect
    return HttpResponseRedirect(redirect)

