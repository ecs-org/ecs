# -*- coding: utf-8 -*-
import datetime
import xlwt
from decimal import Decimal
from StringIO import StringIO

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, InvalidPage

from ecs.utils.decorators import developer
from ecs.users.utils import user_flag_required, sudo
from ecs.utils.security import readonly
from ecs.core.models import Submission
from ecs.checklists.models import Checklist
from ecs.documents.models import Document, DocumentType
from ecs.utils.viewutils import render, render_html
from ecs.ecsmail.utils import deliver, whitewash
from ecs.tasks.models import Task

from ecs.billing.models import Price, ChecklistBillingState, Invoice, ChecklistPayment
from ecs.billing.stats import collect_submission_billing_stats


def _get_address(submission_form, prefix):
    attrs = ('name', 'contact', 'address1', 'address2', 'zip_code', 'city')
    data = dict((attr, getattr(submission_form, '%s_%s' % (prefix, attr), '')) for attr in attrs)
    bits = ['%(name)s' % data, 'zH %s' % data['contact'].full_name]
    if data['address1']:
        bits.append('%(address1)s' % data)
    if data['address2']:
        bits.append('%(address2)s' % data)
    bits.append('%(zip_code)s %(city)s' % data)
    return ", ".join(bits)

def _get_uid_number(submission_form, prefix):
    return getattr(submission_form, '{0}_uid'.format(prefix)) or u'?'
    
def _get_organizations(submission_form):
    organizations = submission_form.investigators.values_list('organisation')
    if len(organizations) == 1:
        return organizations[0][0]
    if len(organizations) > 1:
        return ", ".join("%s (%s)" % (o, i+1) for i, (o,) in enumerate(organizations))
    return ""
    

class SimpleXLS(object):
    def __init__(self, sheet_name=_(u"statistical result")):
        self.xls = xlwt.Workbook(encoding="utf-8")
        self.sheet = self.xls.add_sheet(sheet_name)
        self.sheet.panes_frozen = True
        self.sheet.horz_split_pos = 1
        self.widths = []
        
    def write_row(self, r, cells, header=False):
        for i, cell in enumerate(cells):
            if header:
                style = xlwt.easyxf('font: bold on; align: horiz center;')
                self.sheet.write(r, i, cell, style)
            else:
                self.sheet.write(r, i, cell)

            try:
                if isinstance(cell, (int, long, float, Decimal)):
                    width = len(unicode(cell))
                else:
                    width = len(cell)
            except TypeError:
                width = 0

            if i >= len(self.widths):
                self.widths.append(width)
            else:
                self.widths[i] = max(self.widths[i], width)
            
    def write(self, *args, **kwargs):
        self.sheet.write(*args, **kwargs)
            
    def save(self, f):
        # HACK: the width of the zero character in the default font is 256
        # the default font is proportional, so we apply an arbitraty multiplication
        # factor to get the width right (content with a lot of wide glyphs will
        # still get a wrong width)
        for i, width in enumerate(self.widths):
            self.sheet.col(i).width = int((1 + width) * 256 * 1.1)
        self.xls.save(f)

@readonly(methods=['GET'])
@user_flag_required('is_internal')
def submission_billing(request):
    with sudo():
        categorization_tasks = Task.objects.filter(task_type__workflow_node__uid='categorization_review', closed_at__isnull=False, deleted_at__isnull=True)
        categorized_submissions = Submission.objects.filter(pk__in=categorization_tasks.values('data_id').query)
    unbilled_submissions = list(categorized_submissions.filter(invoice__isnull=True).order_by('ec_number'))
    for submission in unbilled_submissions:
        submission.price = Price.objects.get_for_submission(submission)

    if request.method == 'POST':
        selected_for_billing = []
        for submission in unbilled_submissions:
            if request.POST.get('bill_%s' % submission.pk, False):
                selected_for_billing.append(submission)
                
        xls = SimpleXLS()
        xls.write_row(0, (_(u'amt.'), _(u'EC-Number'), _(u'company'), _(u'UID-Nr.'), _(u'Eudract-Nr.'), _(u'applicant'), _(u'clinic'), _(u'sum')), header=True)
        for i, submission in enumerate(selected_for_billing):
            r = i + 1
            submission_form = submission.current_submission_form
            xls.write_row(i + 1, [
                "%s." % r,
                submission.get_ec_number_display(),
                _get_address(submission_form, submission_form.invoice_name and 'invoice' or 'sponsor'),
                _get_uid_number(submission_form, submission_form.invoice_name and 'invoice' or 'sponsor'),
                submission_form.eudract_number or '?',
                submission_form.submitter_contact.full_name,
                _get_organizations(submission_form),
                submission.price.price,
            ])
        r = len(selected_for_billing) + 1
        xls.write(r, 7, xlwt.Formula('SUM(H2:H%s)' % r))
        xls_buf = StringIO()
        xls.save(xls_buf)
        now = datetime.datetime.now()
        doctype = DocumentType.objects.get(identifier='invoice')
        doc = Document.objects.create_from_buffer(xls_buf.getvalue(), mimetype='application/vnd.ms-excel', date=now, doctype=doctype)

        invoice = Invoice.objects.create(document=doc)
        invoice.submissions = selected_for_billing
        
        return HttpResponseRedirect(reverse('ecs.billing.views.view_invoice', kwargs={'invoice_pk': invoice.pk}))

    return render(request, 'billing/submissions.html', {
        'submissions': unbilled_submissions,
    })

@readonly()
@user_flag_required('is_internal')
def view_invoice(request, invoice_pk=None):
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    return render(request, 'billing/submission_summary.html', {
        'invoice': invoice,
    })

@readonly()
@user_flag_required('is_internal')
def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-created_at')
    paginator = Paginator(invoices, 25)
    try:
        invoices = paginator.page(int(request.GET.get('page', '1')))
    except (EmptyPage, InvalidPage):
        invoices = paginator.page(1)
    return render(request, 'billing/invoice_list.html', {
        'invoices': invoices,
    })

@developer
def reset_external_review_payment(request):
    ChecklistBillingState.objects.update(billed_at=None)
    return HttpResponseRedirect(reverse('ecs.billing.views.external_review_payment'))

@readonly(methods=['GET'])
@user_flag_required('is_internal')
def external_review_payment(request):
    checklists = Checklist.objects.filter(blueprint__slug='external_review').exclude(status='new').filter(
        Q(billing_state__isnull=True)|Q(billing_state__isnull=False, billing_state__billed_at=None))
    price = Price.objects.get_review_price()

    if request.method == 'POST':
        selected_for_payment = []
        for checklist in checklists:
            if request.POST.get('pay_%s' % checklist.pk, False):
                selected_for_payment.append(checklist)
        reviewers = User.objects.filter(pk__in=[c.user.pk for c in selected_for_payment]).distinct()

        xls = SimpleXLS()
        xls.write_row(0, (_(u'amt.'), _(u'reviewer'), _(u'EC-Nr.'), _(u'sum'), _(u'IBAN'), _('SWIFT-BIC'), _('Social Security Number')), header=True)
        for i, reviewer in enumerate(reviewers):
            checklists = reviewer.checklist_set.filter(pk__in=[c.pk for c in selected_for_payment])
            xls.write_row(i + 1, [
                len(checklists),
                unicode(reviewer),
                ", ".join(c.submission.get_ec_number_display() for c in checklists),
                len(checklists) * price.price,
                reviewer.ecs_profile.iban,
                reviewer.ecs_profile.swift_bic,
                reviewer.ecs_profile.social_security_number,
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
        doctype = DocumentType.objects.get(identifier='checklist_payment')
        doc = Document.objects.create_from_buffer(xls_buf.getvalue(), mimetype='application/vnd.ms-excel', date=now, doctype=doctype)

        for checklist in selected_for_payment:
            state, created = ChecklistBillingState.objects.get_or_create(checklist=checklist, defaults={'billed_at': now})
            if not state.billed_at == now:
                state.billed_at = now
                state.save()

        payment = ChecklistPayment.objects.create(document=doc)
        payment.checklists = selected_for_payment

        return HttpResponseRedirect(reverse('ecs.billing.views.view_checklist_payment', kwargs={'payment_pk': payment.pk}))

    return render(request, 'billing/external_review.html', {
        'checklists': checklists,
        'price': price,
    })

@readonly()
@user_flag_required('is_internal')
def view_checklist_payment(request, payment_pk=None):
    payment = get_object_or_404(ChecklistPayment, pk=payment_pk)
    return render(request, 'billing/external_review_summary.html', {
        'payment': payment,
    })

@readonly()
@user_flag_required('is_internal')
def checklist_payment_list(request):
    payments = ChecklistPayment.objects.all().order_by('-created_at')
    paginator = Paginator(payments, 25)
    try:
        payments = paginator.page(int(request.GET.get('page', '1')))
    except (EmptyPage, InvalidPage):
        payments = paginator.page(1)
    return render(request, 'billing/checklist_payment_list.html', {
        'payments': payments,
    })
