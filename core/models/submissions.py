# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericRelation
from django.conf import settings
from django.utils.translation import ugettext as _, ugettext_lazy
from django.contrib.contenttypes.models import ContentType

from ecs.core.models.names import NameField
from ecs.core.parties import get_involved_parties, get_reviewing_parties, get_presenting_parties
from ecs.authorization import AuthorizationManager
from ecs.documents.models import Document
from ecs.utils.common_messages import send_submission_change, send_submission_creation, send_submission_invitation
from ecs.users.utils import get_user, create_phantom_user

MIN_EC_NUMBER = 1000

class SubmissionQuerySet(models.query.QuerySet):
    def amg(self):
        return self.filter(Q(is_amg=True) | (
            Q(is_amg=None) & (
                Q(current_submission_form__project_type_non_reg_drug=True)
                | Q(current_submission_form__project_type_reg_drug=True)
            )
        ))
    
    def mpg(self):
        return self.filter(Q(is_mpg=True) | (
            Q(is_mpg=None) & Q(current_submission_form__project_type_medical_device=True)
        ))

    def b2(self):
        return self.filter(Q(forms__current_published_vote__isnull=False, forms__current_published_vote__result='2')|Q(forms__current_pending_vote__isnull=False, forms__current_pending_vote__result='2'), current_submission_form__isnull=False)

    def new(self):
        return self.filter(meetings__isnull=True)
        
    def thesis(self):
        return self.filter(Q(thesis=True)|~Q(current_submission_form__project_type_education_context=None))

    def next_meeting(self):
        return self.filter(meetings__start__gt=datetime.datetime.now())

    def mine(self, user):
        return self.filter(Q(current_submission_form__submitter=user)|Q(current_submission_form__sponsor=user)|Q(current_submission_form__presenter=user))

    def reviewed_by_user(self, user, include_workflow=True):
        q = self.filter(additional_reviewers=user)
        for a in user.assigned_medical_categories.all():
            q |= a.meeting.submissions.filter(medical_categories=a.category)

        if include_workflow:
            from ecs.tasks.models import Task
            submission_ct = ContentType.objects.get_for_model(Submission)
            q |= self.filter(pk__in=Task.objects.filter(content_type=submission_ct, assigned_to=user).values('data_id').query)

        return q.distinct()
        
        
class SubmissionManager(AuthorizationManager):
    def get_base_query_set(self):
        return SubmissionQuerySet(self.model).distinct()
        
    def amg(self):
        return self.all().amg()
        
    def mpg(self):
        return self.all().mpg()

    def new(self):
        return self.all().new()

    def b2(self):
        return self.all().b2()

    def thesis(self):
        return self.all().thesis()

    def next_meeting(self):
        return self.all().next_meeting()

    def mine(self, user):
        return self.all().mine(user)

    def reviewed_by_user(self, user, include_workflow=True):
        return self.all().reviewed_by_user(user, include_workflow=include_workflow)

class Submission(models.Model):
    ec_number = models.PositiveIntegerField(unique=True, db_index=True)
    keywords = models.TextField(blank=True, null=True)
    medical_categories = models.ManyToManyField('core.MedicalCategory', related_name='submissions', blank=True)
    thesis = models.NullBooleanField()
    retrospective = models.NullBooleanField()
    expedited = models.NullBooleanField()
    expedited_review_categories = models.ManyToManyField('core.ExpeditedReviewCategory', related_name='submissions', blank=True)
    external_reviewer = models.NullBooleanField()
    external_reviewer_name = models.ForeignKey('auth.user', null=True, blank=True, related_name='reviewed_submissions')
    external_reviewer_billed_at = models.DateTimeField(null=True, default=None, blank=True, db_index=True)
    remission = models.NullBooleanField()
    additional_reviewers = models.ManyToManyField(User, blank=True, related_name='additional_review_submission_set')
    sponsor_required_for_next_meeting = models.BooleanField(default=False)
    insurance_review_required = models.NullBooleanField()
    befangene = models.ManyToManyField(User, null=True, related_name='befangen_for_submissions')
    billed_at = models.DateTimeField(null=True, default=None, blank=True, db_index=True)
    transient = models.BooleanField(default=False)
    valid_until = models.DateField(null=True, blank=True)
    
    is_amg = models.NullBooleanField()   # Arzneimittelgesetz
    is_mpg = models.NullBooleanField()   # Medizinproduktegesetz
    
    # denormalization
    current_submission_form = models.OneToOneField('core.SubmissionForm', null=True, related_name='current_for_submission')
    next_meeting = models.ForeignKey('meetings.Meeting', null=True, related_name='_current_for_submissions')
    
    objects = SubmissionManager()
    
    def get_submission(self):
        return self

    def get_ec_number_display(self, short=False, separator=u'/'):
        year, num = divmod(self.ec_number, 10000)
        if short and datetime.datetime.now().year == int(year):
            return unicode(num)
        return u"%s%s%s" % (num, separator, year)
        
    get_ec_number_display.short_description = _('EC-Number')

    def get_befangene(self):
        sf = self.current_submission_form
        emails = filter(None, [sf.sponsor_email, sf.invoice_email, sf.submitter_email] + [x.email for x in sf.investigators.all()])
        return list(User.objects.filter(email__in=emails))

    def get_creation_notification_receivers(self):
        return [], [] # FIXME: wah! (FMD3) why is this function short-cutted?
        sf = self.current_submission_form
        emails = filter(None, [sf.sponsor_email] + [x.email for x in sf.investigators.all()])
        registered = User.objects.filter(email__in=emails)
        unregistered = emails.difference(registered)
        return registered, unregistered
    
    @property
    def notifications(self):
        from ecs.notifications.models import Notification
        return Notification.objects.filter(submission_forms__submission=self)
   
    @property
    def votes(self):
        from ecs.core.models import Vote
        return Vote.objects.filter(submission_form__submission=self)

    @property
    def project_title(self):
        if not self.current_submission_form:
            return None
        return self.current_submission_form.project_title
        
    @property
    def german_project_title(self):
        if not self.current_submission_form:
            return None
        return self.current_submission_form.german_project_title

    def project_title_display(self):
        if self.german_project_title:
            return self.german_project_title
        elif self.project_title:
            return self.project_title
        else:
            return None
        
    @property
    def multicentric(self):
        if not self.current_submission_form:
            return None
        return self.current_submission_form.multicentric
        
    @property
    def is_active(self):
        submission_form = self.current_submission_form
        if submission_form:
            if submission_form.current_published_vote:
                return submission_form.current_published_vote.activates
        return False
        
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

        
    def save(self, **kwargs):
        if not self.ec_number:
            from ecs.users.utils import sudo
            with sudo():
                year = datetime.datetime.now().year
                max_num = Submission.objects.filter(ec_number__range=(year * 10000, (year + 1) * 10000 - 1)).aggregate(models.Max('ec_number'))['ec_number__max']
                if max_num is None:
                    max_num = 10000 * year + MIN_EC_NUMBER
                else:
                    year, num = divmod(max_num, 10000)
                    max_num = year * 10000 + max(num, MIN_EC_NUMBER)
                # XXX: this breaks if there are more than 9999 studies per year (FMD2)
                self.ec_number = max_num + 1
        return super(Submission, self).save(**kwargs)
        
    def __unicode__(self):
        return self.get_ec_number_display()
        
    def update_next_meeting(self):
        next = self.meetings.filter(start__gt=datetime.datetime.now()).order_by('start')[:1]
        if next:
            if next[0].id != self.next_meeting_id:
                self.next_meeting = next[0]
                self.save()
        elif self.next_meeting_id:
            self.next_meeting = None
            self.save()
        
    class Meta:
        app_label = 'core'

SUBMISSION_TYPE_MONOCENTRIC = 1
SUBMISSION_TYPE_MULTICENTRIC = 2
SUBMISSION_TYPE_MULTICENTRIC_LOCAL = 6

SUBMISSION_TYPE_CHOICES = (
    (SUBMISSION_TYPE_MONOCENTRIC, ugettext_lazy('monocentric')), 
    (SUBMISSION_TYPE_MULTICENTRIC, ugettext_lazy('multicentric, main ethics commission')),
    (SUBMISSION_TYPE_MULTICENTRIC_LOCAL, ugettext_lazy('multicentric, local ethics commission')),
)

class SubmissionForm(models.Model):
    submission = models.ForeignKey('core.Submission', related_name="forms")
    acknowledged = models.BooleanField(default=False)
    ethics_commissions = models.ManyToManyField('core.EthicsCommission', related_name='submission_forms', through='Investigator')
    pdf_document = models.OneToOneField(Document, related_name="submission_form", null=True)
    documents = models.ManyToManyField('documents.Document', null=True, related_name='submission_forms')
    is_notification_update = models.BooleanField(default=False)
    transient = models.BooleanField(default=False)

    project_title = models.TextField()
    eudract_number = models.CharField(max_length=60, null=True, blank=True)
    protocol_number = models.CharField(max_length=60, blank=True)
    external_reviewer_suggestions = models.TextField(null=True, blank=True)
    submission_type = models.SmallIntegerField(null=True, blank=True, choices=SUBMISSION_TYPE_CHOICES, default=SUBMISSION_TYPE_MONOCENTRIC)
    presenter = models.ForeignKey(User, related_name='presented_submission_forms')
    created_at = models.DateTimeField(default=datetime.datetime.now)
    
    # denormalization
    primary_investigator = models.OneToOneField('core.Investigator', null=True)
    current_published_vote = models.OneToOneField('core.Vote', null=True, related_name='_currently_published_for')
    current_pending_vote = models.OneToOneField('core.Vote', null=True, related_name='_currently_pending_for')
    
    class Meta:
        app_label = 'core'
        
    objects = AuthorizationManager()
    
    # 1.4 (via self.documents)

    # 1.5
    sponsor = models.ForeignKey(User, null=True, related_name="sponsored_submission_forms")
    sponsor_name = models.CharField(max_length=100, null=True)
    sponsor_contact = NameField()
    sponsor_address = models.CharField(max_length=60, null=True)
    sponsor_zip_code = models.CharField(max_length=10, null=True)
    sponsor_city = models.CharField(max_length=80, null=True)
    sponsor_phone = models.CharField(max_length=30, null=True)
    sponsor_fax = models.CharField(max_length=30, null=True, blank=True)
    sponsor_email = models.EmailField(null=True)
    sponsor_agrees_to_publishing = models.BooleanField(default=True)
    
    invoice = models.ForeignKey(User, null=True, related_name='charged_submission_forms')
    invoice_name = models.CharField(max_length=160, null=True, blank=True)
    invoice_contact = NameField()
    invoice_address = models.CharField(max_length=60, null=True, blank=True)
    invoice_zip_code = models.CharField(max_length=10, null=True, blank=True)
    invoice_city = models.CharField(max_length=80, null=True, blank=True)
    invoice_phone = models.CharField(max_length=50, null=True, blank=True)
    invoice_fax = models.CharField(max_length=45, null=True, blank=True)
    invoice_email = models.EmailField(null=True, blank=True)
    invoice_uid = models.CharField(max_length=35, null=True, blank=True) # 24? need to check
    invoice_uid_verified_level1 = models.DateTimeField(null=True, blank=True) # can be done via EU API
    invoice_uid_verified_level2 = models.DateTimeField(null=True, blank=True) # can be done manually via Tax Authority, local.
    
    # 2.1
    project_type_non_reg_drug = models.BooleanField()
    project_type_reg_drug = models.BooleanField()
    project_type_reg_drug_within_indication = models.BooleanField()
    project_type_reg_drug_not_within_indication = models.BooleanField()
    project_type_medical_method = models.BooleanField()
    project_type_medical_device = models.BooleanField()
    project_type_medical_device_with_ce = models.BooleanField()
    project_type_medical_device_without_ce = models.BooleanField()
    project_type_medical_device_performance_evaluation = models.BooleanField()
    project_type_basic_research = models.BooleanField()
    project_type_genetic_study = models.BooleanField()
    project_type_register = models.BooleanField()
    project_type_biobank = models.BooleanField()
    project_type_retrospective = models.BooleanField()
    project_type_questionnaire = models.BooleanField()
    project_type_education_context = models.SmallIntegerField(null=True, blank=True, choices=[(1, 'Dissertation'), (2, 'Diplomarbeit')])
    project_type_misc = models.TextField(null=True, blank=True)
    project_type_psychological_study = models.BooleanField()
    project_type_nursing_study = models.BooleanField()
    
    # 2.2
    specialism = models.TextField(null=True)

    # 2.3
    pharma_checked_substance = models.TextField(null=True, blank=True)
    pharma_reference_substance = models.TextField(null=True, blank=True)
    
    # 2.4
    medtech_checked_product = models.TextField(null=True, blank=True)
    medtech_reference_substance = models.TextField(null=True, blank=True)

    # 2.5
    clinical_phase = models.CharField(max_length=10)
    
    # 2.6 + 2.7 (via ParticipatingCenter)
    
    # 2.8
    already_voted = models.BooleanField()
    
    # 2.9
    subject_count = models.IntegerField()

    # 2.10
    subject_minage = models.IntegerField()
    subject_maxage = models.IntegerField()
    subject_noncompetents = models.BooleanField()
    subject_males = models.BooleanField()    
    subject_females = models.BooleanField()
    subject_childbearing = models.BooleanField()
    
    # 2.11
    subject_duration = models.CharField(max_length=200)
    subject_duration_active = models.CharField(max_length=200)
    subject_duration_controls = models.CharField(max_length=200, null=True, blank=True)

    # 2.12
    subject_planned_total_duration = models.CharField(max_length=250)

    # 3a
    substance_registered_in_countries = models.ManyToManyField('countries.Country', related_name='submission_forms', blank=True, db_table='submission_registered_countries')
    substance_preexisting_clinical_tries = models.NullBooleanField(blank=True, db_column='existing_tries')
    substance_p_c_t_countries = models.ManyToManyField('countries.Country', blank=True)
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
    study_plan_blind = models.SmallIntegerField(choices=[(0, ugettext_lazy('open')), (1, ugettext_lazy('blind')), (2, ugettext_lazy('double-blind'))])
    study_plan_observer_blinded = models.BooleanField()
    study_plan_randomized = models.BooleanField()
    study_plan_parallelgroups = models.BooleanField()
    study_plan_controlled = models.BooleanField()
    study_plan_cross_over = models.BooleanField()
    study_plan_placebo = models.BooleanField()
    study_plan_factorized = models.BooleanField()
    study_plan_pilot_project = models.BooleanField()
    study_plan_equivalence_testing = models.BooleanField()
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
    study_plan_power = models.CharField(max_length=80)
    study_plan_statalgorithm = models.CharField(max_length=50)
    study_plan_multiple_test_correction_algorithm = models.CharField(max_length=100)
    study_plan_dropout_ratio = models.CharField(max_length=80)
    
    # 8.3
    study_plan_population_intention_to_treat  = models.BooleanField()
    study_plan_population_per_protocol  = models.BooleanField()
    study_plan_abort_crit = models.CharField(max_length=265)
    study_plan_planned_statalgorithm = models.TextField(null=True, blank=True)

    # 8.4
    study_plan_dataquality_checking = models.TextField()
    study_plan_datamanagement = models.TextField()

    # 8.5
    study_plan_biometric_planning = models.CharField(max_length=260)
    study_plan_statistics_implementation = models.CharField(max_length=270)

    # 8.6 (either anonalgorith or reason or dvr may be set.)
    study_plan_dataprotection_reason = models.CharField(max_length=120, blank=True)
    study_plan_dataprotection_dvr = models.CharField(max_length=180, blank=True)
    study_plan_dataprotection_anonalgoritm = models.TextField(null=True, blank=True)
    
    # 9.x
    submitter = models.ForeignKey(User, null=True, related_name='submitted_submission_forms')
    submitter_contact = NameField()
    submitter_email = models.EmailField(blank=False, null=True)
    submitter_organisation = models.CharField(max_length=180)
    submitter_jobtitle = models.CharField(max_length=130)
    submitter_is_coordinator = models.BooleanField()
    submitter_is_main_investigator = models.BooleanField()
    submitter_is_sponsor = models.BooleanField()
    submitter_is_authorized_by_sponsor = models.BooleanField()
    
    date_of_receipt = models.DateField(null=True, blank=True)
    
    def save(self, **kwargs):
        if not self.presenter_id:
            from ecs.users.utils import get_current_user
            user = get_current_user()
            if user:
                self.presenter = user
        for x in ('submitter', 'sponsor', 'invoice'):
            email = getattr(self, '{0}_email'.format(x))
            if email:
                try:
                    user = get_user(email)
                except User.DoesNotExist:
                    user = create_phantom_user(email, role=x)

                setattr(self, x, user)

        return super(SubmissionForm, self).save(**kwargs)
   
    def __unicode__(self):
        return "%s: %s" % (self.submission.get_ec_number_display(), self.project_title)
    
    def get_filename_slice(self):
        return self.submission.get_ec_number_display(separator='_')

    @property
    def multicentric(self):
        return self.investigators.count() > 1
        
    @property
    def monocentric(self):
        return self.investigators.count() == 1
        
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
    def project_type_drug(self):
        return self.project_type_non_reg_drug or self.project_type_reg_drug
        
    @property
    def project_type_medical_device_or_method(self):
        return self.project_type_medical_method or self.project_type_medical_device or self.project_type_medical_device_performance_evaluation
        
    @property
    def protocol(self):
        protocol_doc = self.documents.exclude(status='deleted').filter(doctype__identifier='protocol').order_by('-date', '-version')[:1]
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

    @property
    def current_vote(self):
        return self.current_pending_vote or self.current_published_vote
        
    def get_involved_parties(self, include_workflow=True):
        return get_involved_parties(self, include_workflow=include_workflow)

    def get_presenting_parties(self, include_workflow=True):
        return get_presenting_parties(self, include_workflow=include_workflow)

    def get_reviewing_parties(self, include_workflow=True):
        return get_reviewing_parties(self, include_workflow=include_workflow)


def attach_to_submissions(user):
    for x in ('submitter', 'sponsor', 'invoice'):
        submission_forms = SubmissionForm.objects.filter(**{'{0}_email'.format(x): user.email})
        for sf in submission_forms:
            setattr(sf, x, user)
            sf.save()

    investigator_by_email = Investigator.objects.filter(email=user.email)
    for inv in investigator_by_email:
        inv.user = user
        inv.save()

def _post_submission_form_save(**kwargs):
    from ecs.meetings.models import Meeting, AssignedMedicalCategory

    new_sf = kwargs['instance']
    submission = new_sf.submission
    initial = not submission.current_submission_form
    
    if new_sf.transient:
        return

    if new_sf == submission.current_submission_form:
        old_sf = None
    else:
        old_sf = submission.current_submission_form
        submission.current_submission_form = new_sf

    # set defaults
    if submission.is_amg is None:
        submission.is_amg = new_sf.project_type_drug
    if submission.is_mpg is None:
        submission.is_mpg = new_sf.project_type_medical_device_or_method
    if submission.insurance_review_required is None:
        submission.insurance_review_required = bool(new_sf.insurance_name)
    submission.save(force_update=True)
    
    if initial:
        registered, unregistered = submission.get_creation_notification_receivers()
        send_submission_creation(new_sf, registered)
        send_submission_invitation(new_sf, unregistered)

    if old_sf:
        timetable_entries_q = submission.timetable_entries.all().values('pk').query
        meetings_q = Meeting.objects.filter(timetable_entries__in=timetable_entries_q).values('pk').query
        assigned_medical_categories_q = AssignedMedicalCategory.objects.filter(meeting__in=meetings_q).values('pk').query

                                                                                            # filter for following users:
        recipients_q = Q(username__in=settings.DIFF_REVIEW_LIST)                            # static reviewer list
        recipients_q |= Q(meeting_participations__entry__in=timetable_entries_q)            # assigned to the top
        recipients_q |= Q(assigned_medical_categories__in=assigned_medical_categories_q)    # assigned for medical category
        recipients_q |= Q(email__in=(old_sf.sponsor_email, new_sf.sponsor_email,))          # sponsors

        recipients = list(User.objects.filter(recipients_q).distinct())

        send_submission_change(old_sf, new_sf, recipients);

post_save.connect(_post_submission_form_save, sender=SubmissionForm)


class Investigator(models.Model):
    submission_form = models.ForeignKey(SubmissionForm, related_name='investigators')
    ethics_commission = models.ForeignKey('core.EthicsCommission', null=True, related_name='investigators')
    main = models.BooleanField(default=False, blank=True)

    user = models.ForeignKey(User, null=True, related_name='investigations')
    contact = NameField(required=('first_name', 'last_name',))
    organisation = models.CharField(max_length=80)
    phone = models.CharField(max_length=30, blank=True)
    mobile = models.CharField(max_length=30, blank=True)
    fax = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    jus_practicandi = models.BooleanField(default=False, blank=True)
    specialist = models.CharField(max_length=80, blank=True)
    certified = models.BooleanField(default=False, blank=True)
    subject_count = models.IntegerField()
    
    objects = AuthorizationManager()
    
    class Meta:
        app_label = 'core'


def _post_investigator_save(sender, **kwargs):
    investigator = kwargs['instance']
    if not investigator.main:
        return
    investigator.submission_form.primary_investigator = investigator
    investigator.submission_form.save()
    
post_save.connect(_post_investigator_save, sender=Investigator)

class InvestigatorEmployee(models.Model):
    investigator = models.ForeignKey(Investigator, related_name='employees')

    sex = models.CharField(max_length=1, choices=[("m", ugettext_lazy("Mr")), ("f", ugettext_lazy("Ms")), ("?", "")])
    title = models.CharField(max_length=40)
    surname = models.CharField(max_length=40)
    firstname = models.CharField(max_length=40)
    organisation = models.CharField(max_length=80)
    
    objects = AuthorizationManager()
    
    class Meta:
        app_label = 'core'
    
    @property
    def full_name(self):
        name = []
        if self.title:
            name.append(self.title)
        if self.firstname:
            name.append(self.firstname)
        if self.surname:
            name.append(self.surname)
        return " ".join(name)
    
    @property
    def geschlecht_string(self):
        return dict(m="Hr", f="Fr").get(self.sex, "")
        
    def __unicode__(self):
        return self.full_name


# 6.1 + 6.2
class Measure(models.Model):
    submission_form = models.ForeignKey(SubmissionForm, related_name='measures')
    
    category = models.CharField(max_length=3, choices=[('6.1', ugettext_lazy("only study-related")), ('6.2', ugettext_lazy("for routine purposes"))])
    type = models.CharField(max_length=150)
    count = models.CharField(max_length=150)
    period = models.CharField(max_length=30)
    total = models.CharField(max_length=30)
    
    objects = AuthorizationManager()
    
    class Meta:
        app_label = 'core'


# 3b
class NonTestedUsedDrug(models.Model):
    submission_form = models.ForeignKey(SubmissionForm)

    generic_name = models.CharField(max_length=40)
    preparation_form = models.CharField(max_length=40)
    dosage = models.CharField(max_length=40)
    
    objects = AuthorizationManager()
    
    class Meta:
        app_label = 'core'


# 2.6.2 + 2.7
class ForeignParticipatingCenter(models.Model):
    submission_form = models.ForeignKey(SubmissionForm)
    name = models.CharField(max_length=60)
    investigator_name = models.CharField(max_length=60, blank=True)
    
    objects = AuthorizationManager()
    
    class Meta:
        app_label = 'core'

