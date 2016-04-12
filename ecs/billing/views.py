import xlwt
from decimal import Decimal
from io import BytesIO
import math

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, InvalidPage

from ecs.users.utils import user_group_required, sudo
from ecs.utils.security import readonly
from ecs.core.models import Submission
from ecs.checklists.models import Checklist
from ecs.documents.models import Document
from ecs.documents.views import handle_download
from ecs.tasks.models import Task

from ecs.billing.models import Price, ChecklistBillingState, Invoice, ChecklistPayment


def _get_address(submission_form, prefix):
    attrs = ('name', 'contact', 'address', 'zip_code', 'city')
    data = dict((attr, getattr(submission_form, '%s_%s' % (prefix, attr), '')) for attr in attrs)
    return '{name} z.H. {contact.full_name}, {address}, {zip_code} {city}'.format(**data)

def _get_uid_number(submission_form, prefix):
    return getattr(submission_form, '{0}_uid'.format(prefix)) or '?'
    
def _get_organizations(submission_form):
    organizations = submission_form.investigators.values_list('organisation')
    if len(organizations) == 1:
        return organizations[0][0]
    if len(organizations) > 1:
        return ", ".join("%s (%s)" % (o, i+1) for i, (o,) in enumerate(organizations))
    return ""
    

class SimpleXLS(object):
    def __init__(self, sheet_name=_("statistical result")):
        self.xls = xlwt.Workbook(encoding="utf-8")
        self.sheet = self.xls.add_sheet(sheet_name)
        self.sheet.panes_frozen = True
        self.sheet.horz_split_pos = 1
        self.widths = []
        self.characters = []
        
    def write_row(self, r, cells, header=False):
        for c, cell in enumerate(cells):
            self.write(r, c, cell, header=header)

            try:
                if isinstance(cell, (int, float, Decimal)):
                    width = len(str(cell))
                else:
                    width = len(cell)
            except TypeError:
                width = 0

            if c >= len(self.widths):
                self.widths.append(width)
            else:
                self.widths[c] = max(self.widths[c], width)

            if r >= len(self.characters):
                for i in range(len(self.characters), r+1):
                    self.characters.append(0)
            self.characters[r] = max(self.characters[r], len(str(cell)))
            
    def write(self, r, c, cell, header=False):
        style = xlwt.easyxf('align: wrap on, vert top;')
        if header:
            style = xlwt.easyxf('font: bold on; align: horiz center;')
        self.sheet.write(r, c, cell, style)

    def write_merge(self, r1, r2, c1, c2, cell, header=False):
        style = xlwt.easyxf('align: wrap on, vert top;')
        if header:
            style = xlwt.easyxf('font: bold on; align: horiz center;')
        self.sheet.write_merge(r1, r2, c1, c2, cell, style)
            
    def save(self, f):
        # HACK: the width of the zero character in the default font is 256
        # the default font is proportional, so we apply an arbitraty multiplication
        # factor to get the width right (content with a lot of wide glyphs will
        # still get a wrong width)
        for i, width in enumerate(self.widths):
            self.sheet.col(i).width = min(int((1 + width) * 256 * 1.1), 256*80)
        for i, characters in enumerate(self.characters):
            self.sheet.row(i).height = 255 * int(math.ceil(float(characters)/80))
        self.xls.save(f)

@readonly(methods=['GET'])
@user_group_required('EC-Office', 'EC-Executive Board Member')
def submission_billing(request):
    with sudo():
        categorization_tasks = Task.objects.filter(task_type__workflow_node__uid='categorization_review').closed()
        submissions = Submission.objects.filter(pk__in=categorization_tasks.values('data_id').query)
    unbilled_submissions = list(submissions.filter(invoice__isnull=True).distinct().order_by('ec_number'))
    for submission in unbilled_submissions:
        submission.price = Price.objects.get_for_submission(submission)

    if request.method == 'POST':
        selected_fee = []
        selected_remission = []
        for submission in unbilled_submissions:
            if request.POST.get('bill_%s' % submission.pk, False):
                if submission.remission:
                    selected_remission += [submission]
                else:
                    selected_fee += [submission]
                
        xls = SimpleXLS()
        xls.write_row(0, (_('amt.'), _('EC-Number'), _('company'), _('UID-Nr.'), _('Eudract-Nr.'), _('applicant'), _('clinic'), _('sum')), header=True)
        if selected_fee:
            for i, submission in enumerate(selected_fee, 1):
                r = i
                submission_form = submission.current_submission_form
                xls.write_row(r, [
                    "%s." % i,
                    submission.get_ec_number_display(),
                    _get_address(submission_form, submission_form.invoice_name and 'invoice' or 'sponsor'),
                    _get_uid_number(submission_form, submission_form.invoice_name and 'invoice' or 'sponsor'),
                    submission_form.eudract_number or '?',
                    submission_form.submitter_contact.full_name,
                    _get_organizations(submission_form),
                    submission.price.price,
                ])
            r += 1
            xls.write(r, 7, xlwt.Formula('SUM(H2:H%s)' % r))
            r += 2
        else:
            i = 0
            r = 1
        if selected_remission:
            xls.write_merge(r, r, 0, 2, _('fee-exempted submissions'), header=True)
            for i, submission in enumerate(selected_remission, i+1):
                r += 1
                submission_form = submission.current_submission_form
                xls.write_row(r, [
                    "%s." % i,
                    submission.get_ec_number_display(),
                    _get_address(submission_form, submission_form.invoice_name and 'invoice' or 'sponsor'),
                    _get_uid_number(submission_form, submission_form.invoice_name and 'invoice' or 'sponsor'),
                    submission_form.eudract_number or '?',
                    submission_form.submitter_contact.full_name,
                    _get_organizations(submission_form),
                ])
        xls_buf = BytesIO()
        xls.save(xls_buf)
        doc = Document.objects.create_from_buffer(xls_buf.getvalue(),
            mimetype='application/vnd.ms-excel', doctype='invoice')

        invoice = Invoice.objects.create(document=doc)
        invoice.submissions = selected_fee + selected_remission
        
        return redirect('ecs.billing.views.view_invoice', invoice_pk=invoice.pk)

    return render(request, 'billing/submissions.html', {
        'submissions': unbilled_submissions,
    })

@readonly()
@user_group_required('EC-Office', 'EC-Executive Board Member')
def view_invoice(request, invoice_pk=None):
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    return render(request, 'billing/submission_summary.html', {
        'invoice': invoice,
    })

@readonly()
@user_group_required('EC-Office', 'EC-Executive Board Member')
def invoice_pdf(request, invoice_pk=None):
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    return handle_download(request, invoice.document)

@readonly()
@user_group_required('EC-Office', 'EC-Executive Board Member')
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

@readonly(methods=['GET'])
@user_group_required('EC-Office', 'EC-Executive Board Member')
def external_review_payment(request):
    checklists = Checklist.objects.filter(blueprint__slug='external_review').exclude(status__in=['new', 'dropped']).filter(
        Q(billing_state__isnull=True)|Q(billing_state__isnull=False, billing_state__billed_at=None))
    price = Price.objects.get_review_price()

    if request.method == 'POST':
        selected_for_payment = []
        for checklist in checklists:
            if request.POST.get('pay_%s' % checklist.pk, False):
                selected_for_payment.append(checklist)
        reviewers = User.objects.filter(pk__in=[c.user.pk for c in selected_for_payment]).distinct()

        xls = SimpleXLS()
        xls.write_row(0, (_('amt.'), _('reviewer'), _('EC-Nr.'), _('sum'), _('IBAN'), _('SWIFT-BIC'), _('Social Security Number')), header=True)
        for i, reviewer in enumerate(reviewers):
            checklists = reviewer.checklist_set.filter(pk__in=[c.pk for c in selected_for_payment])
            xls.write_row(i + 1, [
                len(checklists),
                str(reviewer),
                ", ".join(c.submission.get_ec_number_display() for c in checklists),
                len(checklists) * price.price,
                reviewer.profile.iban,
                reviewer.profile.swift_bic,
                reviewer.profile.social_security_number,
            ])
        r = len(reviewers) + 1
        xls.write_row(r, [
            xlwt.Formula('SUM(A2:A%s)' % r),
            "",
            "",
            xlwt.Formula('SUM(D2:D%s)' % r),
        ])

        xls_buf = BytesIO()
        xls.save(xls_buf)
        doc = Document.objects.create_from_buffer(xls_buf.getvalue(),
            mimetype='application/vnd.ms-excel', doctype='checklist_payment')

        for checklist in selected_for_payment:
            ChecklistBillingState.objects.update_or_create(
                checklist=checklist, defaults={'billed_at': doc.date})

        payment = ChecklistPayment.objects.create(document=doc)
        payment.checklists = selected_for_payment

        return redirect('ecs.billing.views.view_checklist_payment', payment_pk=payment.pk)

    return render(request, 'billing/external_review.html', {
        'checklists': checklists,
        'price': price,
    })

@readonly()
@user_group_required('EC-Office', 'EC-Executive Board Member')
def view_checklist_payment(request, payment_pk=None):
    payment = get_object_or_404(ChecklistPayment, pk=payment_pk)
    return render(request, 'billing/external_review_summary.html', {
        'payment': payment,
    })

@readonly()
@user_group_required('EC-Office', 'EC-Executive Board Member')
def checklist_payment_pdf(request, payment_pk=None):
    payment = get_object_or_404(ChecklistPayment, pk=payment_pk)
    return handle_download(request, payment.document)

@readonly()
@user_group_required('EC-Office', 'EC-Executive Board Member')
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
