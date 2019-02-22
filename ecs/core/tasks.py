import os
import time
import hashlib
from io import BytesIO

import xlwt
from celery.task import task, periodic_task
from celery.schedules import crontab

from django.conf import settings
from django.db import transaction
from django.db.models import Min
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.utils import timezone

from ecs.core.models import Submission, SubmissionForm, Investigator
from ecs.core.forms import AllSubmissionsFilterForm
from ecs.core.paper_forms import get_field_info
from ecs.communication.utils import send_system_message_template


@task()
def render_submission_form(submission_form_id=None):
    logger = render_submission_form.get_logger()

    # XXX: Look to wait for submission form to appear. The celery task is
    # triggered on submit before the request transaction is committed, so we
    # have to wait. We should start using transaction.on_commit() as soon as
    # we've updated to Django 1.9.
    for i in range(60):
        with transaction.atomic():
            try:
                sf = SubmissionForm.unfiltered.get(id=submission_form_id)
            except SubmissionForm.DoesNotExist:
                pass
            else:
                sf.render_pdf_document()
                break
        time.sleep(1)
    else:
        logger.error("SubmissionForm(id=%d) didn't appear", submission_form_id)
        return


@task
def xls_export(user_id=None, filters=None):
    user = User.objects.get(id=user_id)

    # Use same filters as selected in the HTML view.
    filterform = AllSubmissionsFilterForm(filters)
    submissions = filterform.filter_submissions(Submission.objects.all(), user)

    submissions = submissions.select_related(
        'current_submission_form',
        'current_submission_form__primary_investigator',
        'current_published_vote',
        'presenter', 'presenter__profile',
    ).prefetch_related(
        'current_submission_form__investigators',
        'current_submission_form__foreignparticipatingcenter_set',
        'medical_categories',
    ).annotate(first_sf_date=Min('forms__created_at')).order_by('ec_number')

    xls = xlwt.Workbook(encoding="utf-8")
    sheet = xls.add_sheet(_('Submissions'))
    sheet.panes_frozen = True
    sheet.horz_split_pos = 3

    header = xlwt.easyxf(
        'font: bold on; align: horiz center, vert center, wrap on;')
    italic = xlwt.easyxf('font: italic on;')

    def label(f):
        return str(get_field_info(SubmissionForm, f).label)

    def inv_label(f):
        return str(get_field_info(Investigator, f).label)

    sheet.write_merge(0, 2, 0, 0, _('EC-Number'), header)
    sheet.write_merge(0, 2, 1, 1, label('project_title'), header)
    sheet.write_merge(0, 2, 2, 2, label('german_project_title'), header)
    sheet.write_merge(0, 2, 3, 3, label('eudract_number'), header)
    sheet.write_merge(0, 1, 4, 5, _('AMG'), header)
    sheet.write(2, 4, _('Yes') + '/' + _('No'), header)
    sheet.write(2, 5, _('Type'), header)
    sheet.write_merge(0, 2, 6, 6, _('MPG'), header)
    sheet.write_merge(0, 2, 7, 7, _('monocentric') + '/' + _('multicentric'),
        header)
    sheet.write_merge(0, 2, 8, 8, _('workflow lane'), header)
    sheet.write_merge(0, 2, 9, 9, _('remission'), header)
    sheet.write_merge(0, 2, 10, 10, _('Medical Categories'), header)
    sheet.write_merge(0, 2, 11, 11, _('Phase'), header)
    sheet.write_merge(0, 1, 12, 13, _('Vote'), header)
    sheet.write(2, 12, _('Vote'), header)
    sheet.write(2, 13, _('valid until'), header)
    sheet.write_merge(0, 2, 14, 14, _('first acknowledged form'), header)
    sheet.write_merge(0, 1, 15, 17, _('Presenter'), header)
    sheet.write(2, 15, _('Organisation'), header)
    sheet.write(2, 16, _('name'), header)
    sheet.write(2, 17, _('email'), header)
    sheet.write_merge(0, 1, 18, 20, _('Submitter'), header)
    sheet.write(2, 18, label('submitter_organisation'), header)
    sheet.write(2, 19, _('contact person'), header)
    sheet.write(2, 20, _('email'), header)
    sheet.write_merge(0, 1, 21, 23, _('Sponsor'), header)
    sheet.write(2, 21, label('sponsor_name'), header)
    sheet.write(2, 22, _('contact person'), header)
    sheet.write(2, 23, _('email'), header)
    sheet.write_merge(0, 1, 24, 26, _('invoice recipient'), header)
    sheet.write(2, 24, label('invoice_name'), header)
    sheet.write(2, 25, _('contact person'), header)
    sheet.write(2, 26, _('email'), header)
    sheet.write_merge(0, 1, 27, 29, _('Primary Investigator'), header)
    sheet.write(2, 27, inv_label('organisation'), header)
    sheet.write(2, 28, _('investigator'), header)
    sheet.write(2, 29, _('email'), header)
    sheet.write_merge(0, 1, 30, 36, _('participants'), header)
    sheet.write(2, 30, label('subject_count'), header)
    sheet.write(2, 31, label('subject_minage'), header)
    sheet.write(2, 32, label('subject_maxage'), header)
    sheet.write(2, 33, label('subject_noncompetents'), header)
    sheet.write(2, 34, label('subject_males'), header)
    sheet.write(2, 35, label('subject_females'), header)
    sheet.write(2, 36, label('subject_childbearing'), header)
    sheet.write_merge(0, 0, 37, 57, _('type of project'), header)
    sheet.write_merge(1, 2, 37, 37, label('project_type_non_reg_drug'), header)
    sheet.write_merge(1, 1, 38, 40, label('project_type_reg_drug'), header)
    sheet.write(2, 38, _('Yes') + '/' + _('No'), header)
    sheet.write(2, 39, label('project_type_reg_drug_within_indication'), header)
    sheet.write(2, 40, label('project_type_reg_drug_not_within_indication'),
        header)
    sheet.write_merge(1, 2, 41, 41, label('project_type_medical_method'),
        header)
    sheet.write_merge(1, 1, 42, 45, label('project_type_medical_device'),
        header)
    sheet.write(2, 42, _('Yes') + '/' + _('No'), header)
    sheet.write(2, 43, label('project_type_medical_device_with_ce'), header)
    sheet.write(2, 44, label('project_type_medical_device_without_ce'), header)
    sheet.write(2, 45,
        label('project_type_medical_device_performance_evaluation'), header)
    sheet.write_merge(1, 2, 46, 46, label('project_type_basic_research'),
        header)
    sheet.write_merge(1, 2, 47, 47, label('project_type_genetic_study'), header)
    sheet.write_merge(1, 2, 48, 48, label('project_type_misc'), header)
    sheet.write_merge(1, 2, 49, 49, label('project_type_education_context'),
        header)
    sheet.write_merge(1, 2, 50, 50, label('project_type_register'), header)
    sheet.write_merge(1, 2, 51, 51, label('project_type_biobank'), header)
    sheet.write_merge(1, 2, 52, 52, label('project_type_retrospective'), header)
    sheet.write_merge(1, 2, 53, 53, label('project_type_questionnaire'), header)
    sheet.write_merge(1, 2, 54, 54, label('project_type_psychological_study'),
        header)
    sheet.write_merge(1, 2, 55, 55, label('project_type_nursing_study'), header)
    sheet.write_merge(1, 2, 56, 56,
        label('project_type_non_interventional_study'), header)
    sheet.write_merge(1, 2, 57, 57, label('project_type_gender_medicine'),
        header)

    # format helpers
    _b = lambda x: _('Yes') if x else _('No')
    _d = lambda x: timezone.localtime(x).strftime('%d.%m.%Y') if x else None

    for i, submission in enumerate(submissions, 3):
        sf = submission.current_submission_form
        vote = submission.current_published_vote
        pi = sf.primary_investigator

        multicentric = (
            sf.investigators.count() +
            sf.foreignparticipatingcenter_set.count()
        ) > 1

        sheet.write(i, 0, submission.get_ec_number_display())
        sheet.write(i, 1, sf.project_title)
        sheet.write(i, 2, sf.german_project_title)
        sheet.write(i, 3, sf.eudract_number)
        sheet.write(i, 4, _b(sf.is_amg))
        sheet.write(i, 5,
            sf.get_submission_type_display() if sf.is_amg else None)
        sheet.write(i, 6, _b(sf.is_mpg))
        sheet.write(i, 7,
            _('multicentric') if multicentric else _('monocentric'))
        sheet.write(i, 8, submission.get_workflow_lane_display())
        sheet.write(i, 9, _b(submission.remission))
        sheet.write(i, 10, ', '.join(sorted(
            m.name for m in submission.medical_categories.all())))
        sheet.write(i, 11, submission.lifecycle_phase)
        sheet.write(i, 12, vote.result if vote else None)
        sheet.write(i, 13, _d(vote.valid_until) if vote else None)
        sheet.write(i, 14, _d(submission.first_sf_date))
        sheet.write(i, 15, submission.presenter.profile.organisation)
        sheet.write(i, 16, str(submission.presenter))
        sheet.write(i, 17, submission.presenter.email)
        sheet.write(i, 18, sf.submitter_organisation)
        sheet.write(i, 19, sf.submitter_contact.full_name)
        sheet.write(i, 20, sf.submitter_email)
        sheet.write(i, 21, sf.sponsor_name)
        sheet.write(i, 22, sf.sponsor_contact.full_name)
        sheet.write(i, 23, sf.sponsor_email)
        if sf.invoice_name:
            sheet.write(i, 24, sf.invoice_name)
            sheet.write(i, 25, sf.invoice_contact.full_name)
            sheet.write(i, 26, sf.invoice_email)
        else:
            sheet.write_merge(i, i, 24, 26, _('same as sponsor'), italic)
        sheet.write(i, 27, pi.organisation)
        sheet.write(i, 28, pi.contact.full_name)
        sheet.write(i, 29, pi.email)
        sheet.write(i, 30, sf.subject_count)
        sheet.write(i, 31, sf.subject_minage)
        sheet.write(i, 32, sf.subject_maxage)
        sheet.write(i, 33, _b(sf.subject_noncompetents))
        sheet.write(i, 34, _b(sf.subject_males))
        sheet.write(i, 35, _b(sf.subject_females))
        sheet.write(i, 36, _b(sf.subject_childbearing))
        sheet.write(i, 37, _b(sf.project_type_non_reg_drug))
        sheet.write(i, 38, _b(sf.project_type_reg_drug))
        sheet.write(i, 39, _b(sf.project_type_reg_drug_within_indication))
        sheet.write(i, 40, _b(sf.project_type_reg_drug_not_within_indication))
        sheet.write(i, 41, _b(sf.project_type_medical_method))
        sheet.write(i, 42, _b(sf.project_type_medical_device))
        sheet.write(i, 43, _b(sf.project_type_medical_device_with_ce))
        sheet.write(i, 44, _b(sf.project_type_medical_device_without_ce))
        sheet.write(i, 45,
            _b(sf.project_type_medical_device_performance_evaluation))
        sheet.write(i, 46, _b(sf.project_type_basic_research))
        sheet.write(i, 47, _b(sf.project_type_genetic_study))
        sheet.write(i, 48, sf.project_type_misc)
        sheet.write(i, 49, sf.get_project_type_education_context_display())
        sheet.write(i, 50, _b(sf.project_type_register))
        sheet.write(i, 51, _b(sf.project_type_biobank))
        sheet.write(i, 52, _b(sf.project_type_retrospective))
        sheet.write(i, 53, _b(sf.project_type_questionnaire))
        sheet.write(i, 54, _b(sf.project_type_psychological_study))
        sheet.write(i, 55, _b(sf.project_type_nursing_study))
        sheet.write(i, 56, _b(sf.project_type_non_interventional_study))
        sheet.write(i, 57, _b(sf.project_type_gender_medicine))

    xls_buf = BytesIO()
    xls.save(xls_buf)
    xls_data = xls_buf.getvalue()

    h = hashlib.sha1()
    h.update(xls_data)

    cache_file = os.path.join(settings.ECS_DOWNLOAD_CACHE_DIR,
        '{}.xls'.format(h.hexdigest()))

    with open(cache_file, 'wb') as f:
        f.write(xls_data)

    send_system_message_template(user, _('XLS-Export done'),
        'submissions/xls_export_done.txt', {'shasum': h.hexdigest()})

# run once per day at 03:28
@periodic_task(run_every=crontab(hour=3, minute=28))
def cull_cache_dir():
    logger = cull_cache_dir.get_logger()
    logger.info("culling download cache")
    for path in os.listdir(settings.ECS_DOWNLOAD_CACHE_DIR):
        if path.startswith('.'):
            continue
        path = os.path.join(settings.ECS_DOWNLOAD_CACHE_DIR, path)
        age = time.time() - os.path.getmtime(path)
        if age > settings.ECS_DOWNLOAD_CACHE_MAX_AGE:
            os.remove(path)
