import datetime
import tempfile
import xlwt
from StringIO import StringIO

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.files import File
from django.conf import settings

from ecs.core.models import Submission, Document
from ecs.core.views.utils import render, render_html
from ecs.messages.mail import send_mail
from ecs.ecsmail.persil import whitewash
from ecs.billing.models import Price


def _get_address(submission_form, prefix):
    attrs = ('name', 'contact_name', 'address1', 'address2', 'zip_code', 'city', 'uid')
    data = dict((attr, getattr(submission_form, '%s_%s' % (prefix, attr), '')) for attr in attrs)
    print data
    bits = ['%(name)s' % data, 'zH %(contact_name)s' % data]
    if data['address1']:
        bits.append('%(address1)s' % data)
    if data['address2']:
        bits.append('%(address2)s' % data)
    bits.append('%(zip_code)s %(city)s' % data)
    if data['uid']:
        bits.append('UID-Nr. %(uid)s' % data)
    return ", ".join(bits)
    
def _get_organizations(submission_form):
    organizations = submission_form.investigators.values_list('organisation')
    if len(organizations) == 1:
        return organizations[0][0]
    if len(organizations) > 1:
        return ", ".join("%s (%s)" % (o, i+1) for i, (o,) in enumerate(organizations))
    return ""

def submission_billing(request):
    # FIXME: only bill accepted submissions
    unbilled_submissions = list(Submission.objects.filter(billed_at=None))
    for submission in unbilled_submissions:
        submission.price = Price.objects.get_for_submission(submission)

    if request.method == 'POST':
        selected_for_billing = []
        for submission in unbilled_submissions:
            if request.POST.get('bill_%s' % submission.pk, False):
                selected_for_billing.append(submission)
                
        xls = xlwt.Workbook(encoding='utf-8')
        sheet = xls.add_sheet(u"Statistikergebnis")
        for i, header in enumerate((u'Anz.', u'Firma', u'Eudract-Nr.', u'Antragsteller', u'Klinik', u'Summe')):
            sheet.write(0, i, header)
        for i, submission in enumerate(selected_for_billing):
            r = i + 1
            submission_form = submission.get_most_recent_form()
            sheet.write(r, 0, "%s." % r)
            sheet.write(r, 1, submission.ec_number)
            sheet.write(r, 2, _get_address(submission_form, submission_form.invoice_name and 'invoice' or 'sponsor'))
            sheet.write(r, 3, submission_form.eudract_number or '?')
            sheet.write(r, 4, submission_form.submitter_name)
            sheet.write(r, 5, _get_organizations(submission_form))
            sheet.write(r, 6, submission.price.price)
        r = len(selected_for_billing) + 1
        sheet.write(r, 6, xlwt.Formula('SUM(G2:G%s)' % r))
        
        xls_buf = StringIO()
        xls.save(xls_buf)

        tmp = tempfile.NamedTemporaryFile()
        tmp.write(xls_buf.getvalue())
        tmp.flush()
        tmp.seek(0)
        doc = Document(date=datetime.datetime.now(), mimetype='application/vnd.ms-excel', file=File(tmp))
        doc.save()
        tmp.close()
        
        now = datetime.datetime.now()
        Submission.objects.filter(pk__in=[s.pk for s in selected_for_billing]).update(billed_at=now)

        for recipient in settings.BILLING_RECIPIENT_LIST:
            htmlmail = unicode(render_html(request, 'billing/email/submissions.html', {}))
            plainmail = whitewash(htmlmail)

            # FIXME: this should go into a celery queue and not be called directly
            send_mail(subject='Billing request', 
                message=plainmail,
                message_html=htmlmail,
                attachments=[('billing-%s.xls' % now.strftime('%Y%m%d-%H%I%S'), xls_buf.getvalue(), 'application/vnd.ms-excel'),],
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient], 
                fail_silently=False
            )
        # return HttpResponse(xls_buf.getvalue(), mimetype='application/vnd.ms-excel')
        return HttpResponseRedirect(reverse('ecs.billing.views.submission_billing'))

    return render(request, 'billing/submissions.html', {
        'submissions': unbilled_submissions,
    })
    

def external_review_billing(request):
    return render(request, 'billing/external_review.html', {
    
    })