# -*- coding: utf-8 -*-
import datetime
import xlwt
from StringIO import StringIO

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User

from ecs.core.models import Submission
from ecs.documents.models import Document
from ecs.utils.viewutils import render, render_html
from ecs.ecsmail.mail import send_mail
from ecs.ecsmail.persil import whitewash

from ecs.billing.models import Price
from ecs.billing.stats import collect_submission_billing_stats


def _get_address(submission_form, prefix):
    attrs = ('name', 'contact', 'address1', 'address2', 'zip_code', 'city', 'uid')
    data = dict((attr, getattr(submission_form, '%s_%s' % (prefix, attr), '')) for attr in attrs)
    bits = ['%(name)s' % data, 'zH %s' % data['contact'].full_name]
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
    

class SimpleXLS(object):
    def __init__(self, sheet_name="Statistikergebnis"):
        self.xls = xlwt.Workbook(encoding="utf-8")
        self.sheet = self.xls.add_sheet(sheet_name)
        self.sheet.panes_frozen = True
        self.sheet.horz_split_pos = 1
        
    def write_row(self, r, cells):
        for i, cell in enumerate(cells):
            self.sheet.write(r, i, cell)
            
    def write(self, *args, **kwargs):
        self.sheet.write(*args, **kwargs)
            
    def save(self, f):
        self.xls.save(f)


# FIXME: for testing purposes only (FMD1)
def reset_submissions(request):
    Submission.objects.update(billed_at=None)
    return HttpResponseRedirect(reverse('ecs.billing.views.submission_billing'))

def submission_billing(request):
    # FIXME: only bill accepted submissions (FMD1)
    unbilled_submissions = list(Submission.objects.filter(billed_at=None))
    for submission in unbilled_submissions:
        submission.price = Price.objects.get_for_submission(submission)

    if request.method == 'POST':
        selected_for_billing = []
        for submission in unbilled_submissions:
            if request.POST.get('bill_%s' % submission.pk, False):
                selected_for_billing.append(submission)
                
        xls = SimpleXLS()
        xls.write_row(0, (u'Anz.', u'EK-Nummer', u'Firma', u'Eudract-Nr.', u'Antragsteller', u'Klinik', u'Summe'))
        for i, submission in enumerate(selected_for_billing):
            r = i + 1
            submission_form = submission.current_submission_form
            xls.write_row(i + 1, [
                "%s." % r,
                submission.get_ec_number_display(),
                _get_address(submission_form, submission_form.invoice_name and 'invoice' or 'sponsor'),
                submission_form.eudract_number or '?',
                submission_form.submitter_contact.full_name,
                _get_organizations(submission_form),
                submission.price.price,
            ])
        r = len(selected_for_billing) + 1
        xls.write(r, 6, xlwt.Formula('SUM(G2:G%s)' % r))
        
        xls_buf = StringIO()
        xls.save(xls_buf)
        now = datetime.datetime.now()
        doc = Document.objects.create_from_buffer(xls_buf.getvalue(), mimetype='application/vnd.ms-excel', date=now)

        Submission.objects.filter(pk__in=[s.pk for s in selected_for_billing]).update(billed_at=now)

        htmlmail = unicode(render_html(request, 'billing/email/submissions.html', {}))
        plainmail = whitewash(htmlmail)

        send_mail(subject='Billing request', 
            message=plainmail,
            message_html=htmlmail,
            attachments=[('billing-%s.xls' % now.strftime('%Y%m%d-%H%I%S'), xls_buf.getvalue(), 'application/vnd.ms-excel'),],
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.BILLING_RECIPIENT_LIST, 
            fail_silently=False
        )

        summary, total = collect_submission_billing_stats(selected_for_billing)
        
        return render(request, 'billing/submission_summary.html', {
            'summary': summary,
            'xls_doc': doc,
            'total': total,
        })
        return HttpResponseRedirect(reverse('ecs.billing.views.submission_billing'))

    return render(request, 'billing/submissions.html', {
        'submissions': unbilled_submissions,
    })
    

# FIXME: for testing purposes only (FMD1)
def reset_external_review_payment(request):
    Submission.objects.update(external_reviewer_billed_at=None)
    return HttpResponseRedirect(reverse('ecs.billing.views.external_review_payment'))


def external_review_payment(request):
    submissions = Submission.objects.filter(external_reviewer=True, external_reviewer_billed_at=None, external_reviewer_name__isnull=False)
    price = Price.objects.get_review_price()

    if request.method == 'POST':
        selected_for_payment = []
        for submission in submissions:
            if request.POST.get('pay_%s' % submission.pk, False):
                selected_for_payment.append(submission)
        reviewers = User.objects.filter(reviewed_submissions__in=selected_for_payment).distinct()
        
        xls = SimpleXLS()
        xls.write_row(0, (u'Anz.', u'Gutachter', u'EK-Nr.', u'Summe'))
        for i, reviewer in enumerate(reviewers):
            submissions = reviewer.reviewed_submissions.filter(pk__in=[s.pk for s in selected_for_payment])
            xls.write_row(i + 1, [
                len(submissions),
                reviewer.get_full_name(),
                ", ".join(s.get_ec_number_display() for s in submissions),
                len(submissions) * price.price,
            ])
        r = len(reviewers) + 1
        xls.write_row(r, [
            xlwt.Formula('SUM(A2:A%s)' % r),
            "",
            "",
            xlwt.Formula('SUM(D2:D%s)' % r),
        ])
        
        xls_buf = StringIO()
        xls.save(xls_buf)
        now = datetime.datetime.now()
        doc = Document.objects.create_from_buffer(xls_buf.getvalue(), mimetype='application/vnd.ms-excel', date=now)
        
        Submission.objects.filter(pk__in=[s.pk for s in selected_for_payment]).update(external_reviewer_billed_at=now)
        
        htmlmail = unicode(render_html(request, 'billing/email/external_review.html', {}))
        plainmail = whitewash(htmlmail)
        
        send_mail(subject='Payment request', 
            message=plainmail,
            message_html=htmlmail,
            attachments=[('externalreview-%s.xls' % now.strftime('%Y%m%d-%H%I%S'), xls_buf.getvalue(), 'application/vnd.ms-excel'),],
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.BILLING_RECIPIENT_LIST, 
            fail_silently=False
        )
        
        return render(request, 'billing/external_review_summary.html', {
            'reviewers': reviewers,
            'xls_doc': doc,
        })

    return render(request, 'billing/external_review.html', {
        'submissions': submissions,
        'price': price,
    })