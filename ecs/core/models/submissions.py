from datetime import timedelta

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils.translation import ugettext as _, ugettext_lazy
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone

from django_countries import countries
from django_countries.fields import CountryField

from ecs.authorization import AuthorizationManager
from ecs.core.models.names import NameField
from ecs.core.models.constants import (
    MIN_EC_NUMBER, SUBMISSION_INFORMATION_PRIVACY_CHOICES, SUBMISSION_LANE_CHOICES, SUBMISSION_LANE_EXPEDITED,
    SUBMISSION_LANE_RETROSPECTIVE_THESIS, SUBMISSION_LANE_LOCALEC, SUBMISSION_LANE_BOARD,
    SUBMISSION_TYPE_CHOICES, SUBMISSION_TYPE_MONOCENTRIC, SUBMISSION_TYPE_MULTICENTRIC_LOCAL,
    SUBMISSION_TYPE_MULTICENTRIC,
)
from ecs.votes.constants import PERMANENT_VOTE_RESULTS, RECESSED_VOTE_RESULTS
from ecs.core.models.managers import (
    SubmissionManager, SubmissionQuerySet, InvestigatorManager,
    TemporaryAuthorizationManager,
)
from ecs.core.parties import get_involved_parties, get_reviewing_parties, get_presenting_parties
from ecs.documents.models import Document
from ecs.users.utils import get_user, create_phantom_user, sudo
from ecs.core.signals import on_study_change
from ecs.votes.models import Vote
from ecs.notifications.models import Notification
from ecs.users.utils import get_current_user
from ecs.utils.viewutils import render_pdf_context
from ecs.tasks.models import Task


class Submission(models.Model):
    ec_number = models.PositiveIntegerField(unique=True, db_index=True)
    medical_categories = models.ManyToManyField('core.MedicalCategory', related_name='submissions', blank=True)
    workflow_lane = models.SmallIntegerField(null=True, choices=SUBMISSION_LANE_CHOICES, db_index=True)
    remission = models.BooleanField(default=False)
    biased_board_members = models.ManyToManyField(User, blank=True, related_name='biased_for_submissions')

    invite_primary_investigator_to_meeting = models.BooleanField(default=False)

    is_transient = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)

    presenter = models.ForeignKey(User, related_name='presented_submissions')
    susar_presenter = models.ForeignKey(User, related_name='susar_presented_submissions')

    # denormalization
    current_submission_form = models.OneToOneField('core.SubmissionForm', null=True, related_name='current_for_submission')
    current_published_vote = models.OneToOneField('votes.Vote', null=True, related_name='_currently_published_for')
    current_pending_vote = models.OneToOneField('votes.Vote', null=True, related_name='_currently_pending_for')

    objects = SubmissionManager()
    unfiltered = SubmissionQuerySet.as_manager()

    @property
    def newest_submission_form(self):
        return self.forms.all().order_by('-pk')[0]

    @property
    def is_expedited(self):
        return self.workflow_lane == SUBMISSION_LANE_EXPEDITED

    @property
    def is_regular(self):
        return self.workflow_lane == SUBMISSION_LANE_BOARD

    @property
    def is_localec(self):
        return self.workflow_lane == SUBMISSION_LANE_LOCALEC

    def get_submission(self):
        return self

    def get_ec_number_display(self, short=False, separator='/'):
        year, num = divmod(self.ec_number, 10000)
        if short and timezone.now().year == int(year):
            return str(num)
        return "%s%s%s" % (num, separator, year)
        
    get_ec_number_display.short_description = ugettext_lazy('EC-Number')

    @property
    def paper_submission_review_task(self):
        try:
            return Task.objects.for_data(self).filter(task_type__workflow_node__uid='paper_submission_review').open()[0]
        except IndexError:
            return None

    @property
    def notifications(self):
        return Notification.objects.filter(submission_forms__submission=self)
   
    @property
    def votes(self):
        return Vote.objects.filter(submission_form__submission=self)

    # XXX: Is this used anywhere?
    @property
    def project_title(self):
        if not self.current_submission_form:
            return None
        return self.current_submission_form.project_title

    # XXX: Is this used anywhere?
    @property
    def german_project_title(self):
        if not self.current_submission_form:
            return None
        return self.current_submission_form.german_project_title

    def project_title_display(self):
        return self.german_project_title or self.project_title

    @property
    def is_active(self):
        vote = self.current_published_vote
        return (vote and vote.is_positive and vote.is_permanent)

    @property
    def lifecycle_phase(self):
        if self.is_finished:
            return _('Finished')
        elif self.is_expired:
            if self.is_localec:
                return _('Unknown (local EC)')
            return _('Expired')
        elif self.is_active:
            if self.is_localec:
                return _('Unknown (local EC)')
            return _('Active')
        elif self.current_submission_form.is_acknowledged:
            return _('Acknowledged')
        return _('New')
        
    @property
    def main_ethics_commission(self):
        if not self.current_submission_form:
            return None
        return self.current_submission_form.main_ethics_commission
        
    @property
    def primary_investigator(self):
        if not self.current_submission_form:
            return None
        return self.current_submission_form.primary_investigator

    @property
    def has_permanent_vote(self):
        return self.votes.filter(result__in=PERMANENT_VOTE_RESULTS, published_at__isnull=False).exists()

    def get_last_recessed_vote(self, top):
        try:
            return self.votes.filter(result__in=RECESSED_VOTE_RESULTS, top__pk__lt=top.pk).order_by('-pk')[0]
        except IndexError:
            return None
            
    def save(self, **kwargs):
        if not self.presenter_id:
            self.presenter = get_current_user()
        if not self.susar_presenter_id:
            self.susar_presenter = get_current_user()
        if not self.ec_number:
            with sudo():
                year = timezone.now().year
                max_num = Submission.objects.filter(ec_number__range=(year * 10000, (year + 1) * 10000 - 1)).aggregate(models.Max('ec_number'))['ec_number__max']
                if max_num is None:
                    max_num = 10000 * year + MIN_EC_NUMBER
                else:
                    year, num = divmod(max_num, 10000)
                    max_num = year * 10000 + max(num, MIN_EC_NUMBER)
                # XXX: this breaks if there are more than 9999 studies per year (FMD2)
                self.ec_number = max_num + 1
        return super().save(**kwargs)
        
    def __str__(self):
        return self.get_ec_number_display()

    def finish(self):
        self.is_finished = True
        self.save(update_fields=('is_finished',))

        Task.unfiltered.for_submission(self).filter(
            task_type__is_dynamic=True).open().mark_deleted()

    def schedule_to_meeting(self):
        visible = self.workflow_lane == SUBMISSION_LANE_BOARD

        def _schedule():
            duration = timedelta(minutes=7, seconds=30)
            if not visible:
                duration = timedelta(minutes=0)
            from ecs.meetings.models import Meeting
            meeting = Meeting.objects.next_schedulable_meeting(self)
            meeting.add_entry(submission=self, duration=duration, visible=visible)
            return meeting

        top = self.timetable_entries.order_by('-meeting__start').first()

        if top is None:
            return _schedule()
        elif top.meeting.started is None:
            duration = top.duration
            if visible and not top.visible:
                duration = timedelta(minutes=7, seconds=30)
            elif not visible:
                duration = timedelta(minutes=0)
            top.refresh(duration=duration, visible=visible)
        else:
            last_vote = self.current_pending_vote or self.current_published_vote
            if last_vote and last_vote.is_recessed:
                return _schedule()
        return top.meeting

    @property
    def is_reschedulable(self):
        return self.meetings.filter(started=None).exists()

    def get_filename_slice(self):
        return self.get_ec_number_display(separator='_')

    def allows_categorization(self):
        return not self.meetings.filter(started__isnull=False, ended=None).exists() and not self.is_active and not self.is_finished

    def allows_dynamic_task_creation(self):
        return not self.is_expired and not self.is_finished and (
            self.current_published_vote is None or
            not self.current_published_vote.is_negative
        )


class MySubmission(models.Model):
    user_id = models.IntegerField()
    submission_id = models.IntegerField()

    class Meta:
        db_table = 'core_mysubmission'
        managed = False


class SubmissionForm(models.Model):
    submission = models.ForeignKey('core.Submission', related_name="forms")
    ethics_commissions = models.ManyToManyField('core.EthicsCommission', related_name='submission_forms', through='Investigator')
    pdf_document = models.OneToOneField(Document, related_name="submission_form", null=True)
    documents = models.ManyToManyField('documents.Document', related_name='submission_forms')
    is_notification_update = models.BooleanField(default=False)
    is_transient = models.BooleanField(default=False)
    is_acknowledged = models.BooleanField(default=False)
    is_old_medtech = models.NullBooleanField(blank=True)

    project_title = models.TextField()
    eudract_number = models.CharField(max_length=60, null=True, blank=True)
    submission_type = models.SmallIntegerField(null=True, blank=True, choices=SUBMISSION_TYPE_CHOICES)
    presenter = models.ForeignKey(User, related_name='presented_submission_forms')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # denormalization
    primary_investigator = models.OneToOneField('core.Investigator', null=True)

    objects = AuthorizationManager()
    unfiltered = models.Manager()
    
    # 1.4 (via self.documents)

    # 1.5
    sponsor = models.ForeignKey(User, null=True, related_name="sponsored_submission_forms")
    sponsor_name = models.CharField(max_length=100, null=True)
    sponsor_contact = NameField(required=('gender', 'first_name', 'last_name',))
    sponsor_address = models.CharField(max_length=60, null=True)
    sponsor_zip_code = models.CharField(max_length=10, null=True)
    sponsor_city = models.CharField(max_length=80, null=True)
    sponsor_phone = models.CharField(max_length=30, null=True)
    sponsor_fax = models.CharField(max_length=30, null=True, blank=True)
    sponsor_email = models.EmailField(null=True)
    sponsor_uid = models.CharField(max_length=35, null=True, blank=True)
    
    invoice_name = models.CharField(max_length=160, null=True, blank=True)
    invoice_contact = NameField()
    invoice_address = models.CharField(max_length=60, null=True, blank=True)
    invoice_zip_code = models.CharField(max_length=10, null=True, blank=True)
    invoice_city = models.CharField(max_length=80, null=True, blank=True)
    invoice_phone = models.CharField(max_length=50, null=True, blank=True)
    invoice_fax = models.CharField(max_length=45, null=True, blank=True)
    invoice_email = models.EmailField(null=True, blank=True)
    invoice_uid = models.CharField(max_length=35, null=True, blank=True) # 24? need to check
    
    # 2.1
    project_type_non_reg_drug = models.BooleanField(default=False)
    project_type_reg_drug = models.BooleanField(default=False)
    project_type_reg_drug_within_indication = models.BooleanField(default=False)
    project_type_reg_drug_not_within_indication = models.BooleanField(default=False)
    project_type_medical_method = models.BooleanField(default=False)
    project_type_medical_device = models.BooleanField(default=False)
    project_type_medical_device_with_ce = models.BooleanField(default=False)
    project_type_medical_device_without_ce = models.BooleanField(default=False)
    project_type_medical_device_performance_evaluation = models.BooleanField(default=False)
    project_type_basic_research = models.BooleanField(default=False)
    project_type_genetic_study = models.BooleanField(default=False)
    project_type_register = models.BooleanField(default=False)
    project_type_biobank = models.BooleanField(default=False)
    project_type_retrospective = models.BooleanField(default=False)
    project_type_questionnaire = models.BooleanField(default=False)
    project_type_education_context = models.SmallIntegerField(null=True, blank=True, choices=[(1, 'Dissertation'), (2, 'Diplomarbeit')])
    project_type_misc = models.TextField(null=True, blank=True)
    project_type_psychological_study = models.BooleanField(default=False)
    project_type_nursing_study = models.BooleanField(default=False)
    project_type_non_interventional_study = models.BooleanField(default=False)
    project_type_gender_medicine = models.BooleanField(default=False)
    
    # 2.2
    specialism = models.TextField(null=True)

    # 2.3
    pharma_checked_substance = models.TextField(null=True, blank=True)
    pharma_reference_substance = models.TextField(null=True, blank=True)
    
    # 2.4
    medtech_checked_product = models.TextField(null=True, blank=True)
    medtech_reference_substance = models.TextField(null=True, blank=True)

    # 2.5
    clinical_phase = models.CharField(max_length=10, null=True, blank=True)
    
    # 2.6 + 2.7 (via ParticipatingCenter)
    
    # 2.8
    already_voted = models.BooleanField(default=False)
    
    # 2.9
    subject_count = models.PositiveIntegerField()

    # 2.10
    subject_minage = models.PositiveIntegerField(null=True, blank=True)
    subject_maxage = models.PositiveIntegerField(null=True, blank=True)
    subject_noncompetents = models.BooleanField(default=False)
    subject_males = models.BooleanField(default=False)
    subject_females = models.BooleanField(default=False)
    subject_childbearing = models.BooleanField(default=False)
    
    # 2.11
    subject_duration = models.CharField(max_length=200)
    subject_duration_active = models.CharField(max_length=200)
    subject_duration_controls = models.CharField(max_length=200, null=True, blank=True)

    # 2.12
    subject_planned_total_duration = models.CharField(max_length=250)

    # 3a
    substance_registered_in_countries = ArrayField(CountryField(), default=list)
    substance_preexisting_clinical_tries = models.NullBooleanField(blank=True, db_column='existing_tries')
    substance_p_c_t_countries = ArrayField(CountryField(), default=list)
    substance_p_c_t_phase = models.CharField(max_length=80, null=True, blank=True)
    substance_p_c_t_period = models.TextField(null=True, blank=True)
    substance_p_c_t_application_type = models.CharField(max_length=145, null=True, blank=True)
    substance_p_c_t_gcp_rules = models.NullBooleanField(blank=True)
    substance_p_c_t_final_report = models.NullBooleanField(blank=True)
    
    # 3b (via NonTestedUsedDrugs)
    
    # 4.x
    medtech_product_name = models.CharField(max_length=210, null=True, blank=True)
    medtech_manufacturer = models.CharField(max_length=80, null=True, blank=True)
    medtech_certified_for_exact_indications = models.NullBooleanField(blank=True)
    medtech_certified_for_other_indications = models.NullBooleanField(blank=True)
    medtech_ce_symbol = models.NullBooleanField(blank=True)
    medtech_manual_included = models.NullBooleanField(blank=True)
    medtech_technical_safety_regulations = models.TextField(null=True, blank=True)
    medtech_departure_from_regulations = models.TextField(null=True, blank=True)
    
    # 5.x
    insurance_not_required = models.BooleanField(default=False)
    insurance_name = models.CharField(max_length=125, null=True, blank=True)
    insurance_address = models.CharField(max_length=80, null=True, blank=True)
    insurance_phone = models.CharField(max_length=30, null=True, blank=True)
    insurance_contract_number = models.CharField(max_length=60, null=True, blank=True)
    insurance_validity = models.CharField(max_length=60, null=True, blank=True)
    
    # 6.1 + 6.2 (via Measure)

    # 6.3
    additional_therapy_info = models.TextField(blank=True)

    # 7.x
    german_project_title = models.TextField(null=True)
    german_summary = models.TextField(null=True)
    german_preclinical_results = models.TextField(null=True)
    german_primary_hypothesis = models.TextField(null=True)
    german_inclusion_exclusion_crit = models.TextField(null=True)
    german_ethical_info = models.TextField(null=True)
    german_protected_subjects_info = models.TextField(null=True, blank=True)
    german_recruitment_info = models.TextField(null=True)
    german_consent_info = models.TextField(null=True)
    german_risks_info = models.TextField(null=True)
    german_benefits_info = models.TextField(null=True)
    german_relationship_info = models.TextField(null=True)
    german_concurrent_study_info = models.TextField(null=True)
    german_sideeffects_info = models.TextField(null=True)
    german_statistical_info = models.TextField(null=True, blank=True)
    german_dataprotection_info = models.TextField(null=True, blank=True)
    german_aftercare_info = models.TextField(null=True)
    german_payment_info = models.TextField(null=True)
    german_abort_info = models.TextField(null=True)
    german_dataaccess_info = models.TextField(null=True, blank=True)
    german_financing_info = models.TextField(null=True, blank=True)
    german_additional_info = models.TextField(null=True, blank=True)
    
    # 8.1
    study_plan_blind = models.SmallIntegerField(choices=[(0, ugettext_lazy('open')), (1, ugettext_lazy('blind')), (2, ugettext_lazy('double-blind')), (3, ugettext_lazy('not applicable'))])
    study_plan_observer_blinded = models.BooleanField(default=False)
    study_plan_randomized = models.BooleanField(default=False)
    study_plan_parallelgroups = models.BooleanField(default=False)
    study_plan_controlled = models.BooleanField(default=False)
    study_plan_cross_over = models.BooleanField(default=False)
    study_plan_placebo = models.BooleanField(default=False)
    study_plan_factorized = models.BooleanField(default=False)
    study_plan_pilot_project = models.BooleanField(default=False)
    study_plan_equivalence_testing = models.BooleanField(default=False)
    study_plan_misc = models.TextField(null=True, blank=True)
    study_plan_number_of_groups = models.TextField(null=True, blank=True)
    study_plan_stratification = models.TextField(null=True, blank=True)
    study_plan_sample_frequency = models.TextField(null=True, blank=True) 
    study_plan_primary_objectives = models.TextField(null=True, blank=True)
    study_plan_null_hypothesis = models.TextField(null=True, blank=True)
    study_plan_alternative_hypothesis = models.TextField(null=True, blank=True)
    study_plan_secondary_objectives = models.TextField(null=True, blank=True)

    # 8.2
    study_plan_alpha = models.CharField(max_length=80)
    study_plan_alpha_sided = models.SmallIntegerField(choices=[(0, ugettext_lazy('single-sided')), (1, ugettext_lazy('double-sided'))], null=True, blank=True)
    study_plan_power = models.CharField(max_length=80)
    study_plan_statalgorithm = models.CharField(max_length=80)
    study_plan_multiple_test = models.BooleanField(default=False)
    study_plan_multiple_test_correction_algorithm = models.CharField(max_length=100, null=True, blank=True)
    study_plan_dropout_ratio = models.CharField(max_length=80)
    
    # 8.3
    study_plan_population_intention_to_treat  = models.BooleanField(default=False)
    study_plan_population_per_protocol  = models.BooleanField(default=False)
    study_plan_interim_evaluation = models.BooleanField(default=False)
    study_plan_abort_crit = models.CharField(max_length=265, null=True, blank=True)
    study_plan_planned_statalgorithm = models.TextField(null=True, blank=True)

    # 8.4
    study_plan_dataquality_checking = models.TextField()
    study_plan_datamanagement = models.TextField()

    # 8.5
    study_plan_biometric_planning = models.CharField(max_length=260)
    study_plan_statistics_implementation = models.CharField(max_length=270)

    # 8.6 (either anonalgorith or reason or dvr may be set.)
    study_plan_dataprotection_choice = models.CharField(max_length=15, choices=SUBMISSION_INFORMATION_PRIVACY_CHOICES, default='non-personal')
    study_plan_dataprotection_reason = models.CharField(max_length=120, null=True, blank=True)
    study_plan_dataprotection_dvr = models.CharField(max_length=180, null=True, blank=True)
    study_plan_dataprotection_anonalgoritm = models.TextField(null=True, blank=True)
    
    # 9.x
    submitter = models.ForeignKey(User, null=True, related_name='submitted_submission_forms')
    submitter_contact = NameField(required=('gender', 'first_name', 'last_name',))
    submitter_email = models.EmailField(blank=False, null=True)
    submitter_organisation = models.CharField(max_length=180)
    submitter_jobtitle = models.CharField(max_length=130)
    submitter_is_coordinator = models.BooleanField(default=False)
    submitter_is_main_investigator = models.BooleanField(default=False)
    submitter_is_sponsor = models.BooleanField(default=False)
    submitter_is_authorized_by_sponsor = models.BooleanField(default=False)
    
    def save(self, **kwargs):
        if not self.presenter_id:
            self.presenter = get_current_user()
        if not self.submission.is_transient:
            for x, org in (('submitter', 'submitter_organisation'), ('sponsor', 'sponsor_name')):
                email = getattr(self, '{0}_email'.format(x))
                if email:
                    try:
                        user = get_user(email)
                    except User.DoesNotExist:
                        user = create_phantom_user(email, role=x)
                        user.first_name = getattr(self, '{0}_contact_first_name'.format(x))
                        user.last_name = getattr(self, '{0}_contact_last_name'.format(x))
                        user.save()
                        profile = user.profile
                        profile.title = getattr(self, '{0}_contact_title'.format(x))
                        profile.gender = getattr(self, '{0}_contact_gender'.format(x)) or 'f'
                        profile.organisation = getattr(self, org)
                        profile.save()
                    setattr(self, x, user)
        return super().save(**kwargs)

    def render_pdf(self):
        return render_pdf_context('submissions/pdf/view.html', {
            'submission_form': self,
            'documents': self.documents.order_by('doctype__identifier', 'date', 'name'),
        })

    def render_pdf_document(self):
        assert self.pdf_document is None
        pdfdata = self.render_pdf()
        name = 'ek' # -%s' % self.submission.get_ec_number_display(separator='-')
        filename = 'ek-%s' % self.submission.get_ec_number_display(separator='-')
        self.pdf_document = Document.objects.create_from_buffer(pdfdata,
            doctype='submissionform', parent_object=self, name=name,
            original_file_name=filename, version=str(self.version))
        self.save(update_fields=('pdf_document',))

    @property
    def version(self):
        assert self.pk is not None      # already saved
        return self.submission.forms.filter(created_at__lte=self.created_at).count()

    def __str__(self):
        return "%s: %s" % (self.submission.get_ec_number_display(), self.german_project_title or self.project_title)
    
    def get_filename_slice(self):
        return self.submission.get_filename_slice()
        
    @property
    def is_current(self):
        return self.submission.current_submission_form_id == self.id

    def acknowledge(self, choice):
        self.is_acknowledged = choice
        self.save(update_fields=('is_acknowledged',))
        
    def mark_current(self):
        self.submission.current_submission_form = self
        self.submission.save(update_fields=('current_submission_form',))
        
    def allows_edits(self, user):
        s = self.submission
        return s.presenter == user and self.is_current and not s.has_permanent_vote and not s.is_finished

    def allows_resubmission(self, user):
        s = self.submission
        with sudo():
            if s.meetings.filter(started__isnull=False, ended=None).exists():
                return False
        pending_vote = s.current_pending_vote
        has_unpublished_vote = pending_vote and not pending_vote.is_draft
        return self.allows_edits(user) and not has_unpublished_vote
        
    def allows_amendments(self, user):
        s = self.submission
        if s.presenter == user and self.is_current:
            diff_notifications = Notification.objects.filter(submission_forms__submission=self.submission, type__includes_diff=True)
            if not diff_notifications.pending().exists():
                return s.is_active
        return False

    @property
    def is_amg(self):
        return self.project_type_drug

    @property
    def is_mpg(self):
        return self.project_type_medical_device

    @property
    def is_thesis(self):
        return self.project_type_education_context is not None

    @property
    def is_multicentric(self):
        return (
            self.is_categorized_multicentric_and_main or
            self.is_categorized_multicentric_and_local or
            (
                bool(self.non_system_ec_investigators)  # prefetch
                if hasattr(self, 'non_system_ec_investigators')
                else self.investigators.non_system_ec().exists()
            ) or
            self.participatingcenternonsubject_set.exists() or
            self.foreignparticipatingcenter_set.exists()
        )
        
    @property
    def is_monocentric(self):
        return not self.is_multicentric

    @property
    def is_categorized_monocentric(self):
        return self.submission_type == SUBMISSION_TYPE_MONOCENTRIC
        
    @property
    def is_categorized_multicentric_and_local(self):
        return self.submission_type == SUBMISSION_TYPE_MULTICENTRIC_LOCAL
        
    @property
    def is_categorized_multicentric_and_main(self):
        return self.submission_type == SUBMISSION_TYPE_MULTICENTRIC
    
    @property
    def includes_minors(self):
        if self.subject_minage is None:
            return None
        return 0 <= self.subject_minage < 18
    
    @property
    def study_plan_open(self):
        return self.study_plan_blind == 0

    @property
    def study_plan_single_blind(self):
        return self.study_plan_blind == 1

    @property
    def study_plan_double_blind(self):
        return self.study_plan_blind == 2

    @property
    def study_plan_not_applicable(self):
        return self.study_plan_blind == 3

    @property
    def study_plan_alpha_single_sided(self):
        return self.study_plan_alpha_sided == 0

    @property
    def study_plan_alpha_double_sided(self):
        return self.study_plan_alpha_sided == 1
        
    @property
    def project_type_drug(self):
        return self.project_type_non_reg_drug or self.project_type_reg_drug
        
    @property
    def project_type_medical_device_or_method(self):
        return self.project_type_medical_method or self.project_type_medical_device or self.project_type_medical_device_performance_evaluation
        
    @property
    def protocol(self):
        ''' FIXME: still used? '''
        protocol_doc = self.documents.filter(doctype__identifier='protocol').order_by('-date', '-version')[:1]
        if protocol_doc:
            return protocol_doc[0]
        else:
            return None

    @property
    def project_type_education_context_phd(self):
        return self.project_type_education_context == 1

    @property
    def project_type_education_context_master(self):
        return self.project_type_education_context == 2

    @property
    def measures_study_specific(self):
        return self.measures.filter(category="6.1")
    
    @property
    def measures_nonspecific(self):
        return self.measures.filter(category="6.2")
        
    @property
    def main_ethics_commission(self):
        try:
            return self.primary_investigator.ethics_commission
        except Investigator.DoesNotExist:
            return None

    def get_involved_parties(self):
        current_user = get_current_user()
        if current_user and not current_user.profile.is_internal and Task.objects.for_submission(self.submission).filter(task_type__workflow_node__uid='external_review', assigned_to=current_user, deleted_at=None).exists():
            return get_reviewing_parties(self)
        return get_involved_parties(self)

    def get_presenting_parties(self):
        return get_presenting_parties(self)

    def get_reviewing_parties(self, active=None):
        return get_reviewing_parties(self, active=active)

    @property
    def additional_investigators(self):
        additional_investigators = self.investigators.all()
        if self.primary_investigator:
            additional_investigators = additional_investigators.exclude(pk=self.primary_investigator.pk)
        return additional_investigators

    def get_type_display(self):
        bits = []
        if self.is_amg:
            bits.append('{0}({1})'.format(_('AMG'), self.get_submission_type_display()))
        if self.is_mpg:
            old_text = ' alt' if self.is_old_medtech else ''
            bits.append('{0}{1}({2})'.format(_('MPG'), old_text, self.get_submission_type_display()))
        if self.is_thesis:
            bits.append(self.get_project_type_education_context_display())
        if self.includes_minors:
            bits.append(_('minors'))
        if self.submission.invite_primary_investigator_to_meeting and self.submission.timetable_entries.filter(meeting__ended=None).exists():
            bits.append(_('Investigator invited'))
        if self.project_type_non_interventional_study:
            bits.append(_('NIS'))
        return ', '.join(bits)

    def get_substance_registered_in_countries_display(self):
        c = [str(countries.name(c)) for c in self.substance_registered_in_countries]
        return ', '.join(sorted(c))

    def get_substance_p_c_t_countries_display(self):
        c = [str(countries.name(c)) for c in self.substance_p_c_t_countries]
        return ', '.join(sorted(c))
    
    @property
    def study_plan_dataprotection_none(self):
        return self.study_plan_dataprotection_choice == 'personal'

    @property
    def study_plan_dataprotection_partial(self):
        return self.study_plan_dataprotection_choice == 'non-personal'

    @property
    def study_plan_dataprotection_full(self):
        return self.study_plan_dataprotection_choice == 'anonymous'


@receiver(post_save, sender=SubmissionForm)
def _post_submission_form_save(**kwargs):
    new_sf = kwargs['instance']

    if not kwargs['created'] or new_sf.is_transient:
        return

    submission = new_sf.submission
    old_sf = submission.current_submission_form
    
    if not old_sf:
        new_sf.mark_current()
        if new_sf.is_amg:
            submission.invite_primary_investigator_to_meeting = True
        if new_sf.is_thesis:
            submission.remission = True
            submission.workflow_lane = SUBMISSION_LANE_RETROSPECTIVE_THESIS
        elif new_sf.is_categorized_multicentric_and_local:
            submission.workflow_lane = SUBMISSION_LANE_LOCALEC
        submission.save(update_fields=(
            'invite_primary_investigator_to_meeting', 'remission',
            'workflow_lane',
        ))

    on_study_change.send(Submission, submission=submission, old_form=old_sf, new_form=new_sf)


class Investigator(models.Model):
    submission_form = models.ForeignKey(SubmissionForm, related_name='investigators')
    ethics_commission = models.ForeignKey('core.EthicsCommission', related_name='investigators')
    main = models.BooleanField(default=True, blank=True)

    user = models.ForeignKey(User, null=True, related_name='investigations')
    contact = NameField(required=('gender', 'first_name', 'last_name',))
    organisation = models.CharField(max_length=80)
    phone = models.CharField(max_length=30, blank=True)
    mobile = models.CharField(max_length=30, blank=True)
    fax = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=False)
    jus_practicandi = models.BooleanField(default=False, blank=True)
    specialist = models.CharField(max_length=80, blank=True)
    certified = models.BooleanField(default=False, blank=True)
    subject_count = models.PositiveIntegerField()
    
    objects = InvestigatorManager()
    
    class Meta:
        ordering = ['-main', 'id']

    def save(self, **kwargs):
        if self.email and not self.submission_form.submission.is_transient:
            try:
                user = get_user(self.email)
            except User.DoesNotExist:
                user = create_phantom_user(self.email, role='investigator')
                user.first_name = self.contact_first_name
                user.last_name = self.contact_last_name
                user.save()
                profile = user.profile
                profile.title = self.contact_title
                profile.gender = self.contact_gender
                profile.organisation = self.organisation
                profile.save()
            self.user = user
        return super().save(**kwargs)


@receiver(post_save, sender=Investigator)
def _post_investigator_save(sender, **kwargs):
    investigator = kwargs['instance']
    if investigator.main:
        sf = investigator.submission_form
        sf.primary_investigator = investigator
        sf.save(update_fields=('primary_investigator',))
    

class InvestigatorEmployee(models.Model):
    investigator = models.ForeignKey(Investigator, related_name='employees')

    sex = models.CharField(max_length=1, choices=[("m", ugettext_lazy("Mr")), ("f", ugettext_lazy("Ms"))])
    title = models.CharField(max_length=40, blank=True)
    firstname = models.CharField(max_length=40)
    surname = models.CharField(max_length=40)
    organisation = models.CharField(max_length=80)

    class Meta:
        ordering = ['id']
    
    @property
    def full_name(self):
        name = [self.firstname, self.surname]
        if self.title:
            name.insert(0, self.title)
        return ' '.join(name)

    def __str__(self):
        return self.full_name


# 6.1 + 6.2
class Measure(models.Model):
    submission_form = models.ForeignKey(SubmissionForm, related_name='measures')
    
    category = models.CharField(max_length=3, choices=[('6.1', ugettext_lazy("only study-related")), ('6.2', ugettext_lazy("for routine purposes"))])
    type = models.CharField(max_length=150)
    count = models.CharField(max_length=150)
    period = models.CharField(max_length=30)
    total = models.CharField(max_length=30)

    class Meta:
        ordering = ['id']


# 3b
class NonTestedUsedDrug(models.Model):
    submission_form = models.ForeignKey(SubmissionForm)

    generic_name = models.CharField(max_length=40)
    preparation_form = models.CharField(max_length=40)
    dosage = models.CharField(max_length=40)

    class Meta:
        ordering = ['id']


class ParticipatingCenterNonSubject(models.Model):
    submission_form = models.ForeignKey(SubmissionForm)
    name = models.CharField(max_length=60)
    ethics_commission = models.ForeignKey('core.EthicsCommission')
    investigator_name = models.CharField(max_length=60, blank=True)

    class Meta:
        ordering = ['id']


# 2.6.2 + 2.7
class ForeignParticipatingCenter(models.Model):
    submission_form = models.ForeignKey(SubmissionForm)
    name = models.CharField(max_length=60)
    investigator_name = models.CharField(max_length=60, blank=True)

    class Meta:
        ordering = ['id']


class TemporaryAuthorization(models.Model):
    submission = models.ForeignKey(Submission, related_name='temp_auth')
    user = models.ForeignKey(User, related_name='temp_submission_auth')
    start = models.DateTimeField()
    end = models.DateTimeField()

    objects = TemporaryAuthorizationManager()

    @property
    def is_active(self):
        return self.start <= timezone.now() < self.end
        

