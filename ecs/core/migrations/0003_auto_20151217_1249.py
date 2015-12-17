# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('countries', '__first__'),
        ('core', '0002_auto_20151217_1249'),
    ]

    operations = [
        migrations.AddField(
            model_name='submissionform',
            name='documents',
            field=models.ManyToManyField(related_name='submission_forms', null=True, to='documents.Document'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submissionform',
            name='ethics_commissions',
            field=models.ManyToManyField(related_name='submission_forms', through='core.Investigator', to='core.EthicsCommission'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submissionform',
            name='pdf_document',
            field=models.OneToOneField(related_name='submission_form', null=True, to='documents.Document'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submissionform',
            name='presenter',
            field=models.ForeignKey(related_name='presented_submission_forms', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submissionform',
            name='primary_investigator',
            field=models.OneToOneField(null=True, to='core.Investigator'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submissionform',
            name='sponsor',
            field=models.ForeignKey(related_name='sponsored_submission_forms', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submissionform',
            name='submission',
            field=models.ForeignKey(related_name='forms', to='core.Submission'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submissionform',
            name='submitter',
            field=models.ForeignKey(related_name='submitted_submission_forms', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submissionform',
            name='substance_p_c_t_countries',
            field=models.ManyToManyField(to='countries.Country', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submissionform',
            name='substance_registered_in_countries',
            field=models.ManyToManyField(related_name='submission_forms', db_table=b'submission_registered_countries', to='countries.Country', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submission',
            name='befangene',
            field=models.ManyToManyField(related_name='befangen_for_submissions', null=True, to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submission',
            name='current_submission_form',
            field=models.OneToOneField(related_name='current_for_submission', null=True, to='core.SubmissionForm'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submission',
            name='expedited_review_categories',
            field=models.ManyToManyField(related_name='submissions', to='core.ExpeditedReviewCategory', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submission',
            name='external_reviewers',
            field=models.ManyToManyField(related_name='external_review_submission_set', to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submission',
            name='medical_categories',
            field=models.ManyToManyField(related_name='submissions', to='core.MedicalCategory', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submission',
            name='presenter',
            field=models.ForeignKey(related_name='presented_submissions', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submission',
            name='susar_presenter',
            field=models.ForeignKey(related_name='susar_presented_submissions', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nontesteduseddrug',
            name='submission_form',
            field=models.ForeignKey(to='core.SubmissionForm'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='medicalcategory',
            name='users',
            field=models.ManyToManyField(related_name='medical_categories', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='measure',
            name='submission_form',
            field=models.ForeignKey(related_name='measures', to='core.SubmissionForm'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='investigatoremployee',
            name='investigator',
            field=models.ForeignKey(related_name='employees', to='core.Investigator'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='investigator',
            name='ethics_commission',
            field=models.ForeignKey(related_name='investigators', to='core.EthicsCommission', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='investigator',
            name='submission_form',
            field=models.ForeignKey(related_name='investigators', to='core.SubmissionForm'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='investigator',
            name='user',
            field=models.ForeignKey(related_name='investigations', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='foreignparticipatingcenter',
            name='submission_form',
            field=models.ForeignKey(to='core.SubmissionForm'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='expeditedreviewcategory',
            name='users',
            field=models.ManyToManyField(related_name='expedited_review_categories', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='advancedsettings',
            name='default_contact',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.RunSQL('''
create or replace view core_mysubmission as (
  select distinct
    unnest(array[
      s.presenter_id, s.susar_presenter_id,
      sf.submitter_id, sf.sponsor_id, inv.user_id
    ]) as user_id,
    s.id as submission_id
  from core_submission s
  left join core_submissionform sf on sf.id = s.current_submission_form_id
  left join core_investigator inv on inv.id = sf.primary_investigator_id
)
        '''),
    ]
