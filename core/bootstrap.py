# -*- coding: utf-8 -*-
import os, random
from datetime import datetime

from django.core.management.base import CommandError
from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.core.files import File

from ecs import bootstrap
from ecs.core.models import ExpeditedReviewCategory, Submission, MedicalCategory, EthicsCommission, ChecklistBlueprint, ChecklistQuestion, Investigator, SubmissionForm, Checklist, ChecklistAnswer
from ecs.notifications.models import NotificationType
from ecs.utils.countries.models import Country
from ecs.utils import Args
from ecs.users.utils import sudo
from ecs.documents.models import Document, DocumentType
from ecs.workflow.patterns import Generic
from ecs.integration.utils import setup_workflow_graph


@bootstrap.register()
def default_site():
    ''' XXX: default_site is needed for dbtemplates '''
    Site.objects.get_or_create(pk=1)

@bootstrap.register(depends_on=('ecs.core.bootstrap.default_site',))
def templates():
    from dbtemplates.models import Template
    basedir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    for dirpath, dirnames, filenames in os.walk(basedir):
        if 'xhtml2pdf' not in dirpath:
            continue
        for filename in filenames:
            if filename.startswith('.'):
                continue
            _, ext = os.path.splitext(filename)
            if ext in ('.html', '.inc'):
                path = os.path.join(dirpath, filename)
                name = "db%s" % path.replace(basedir, '').replace('\\', '/')
                content = open(path, 'r').read()
                tpl, created = Template.objects.get_or_create(name=name, defaults={'content': content})
                if not created and tpl.last_changed < datetime.fromtimestamp(os.path.getmtime(path)):
                    tpl.content = content
                    tpl.save()

@bootstrap.register(depends_on=('ecs.integration.bootstrap.workflow_sync', 'ecs.core.bootstrap.checklist_blueprints'))
def submission_workflow():
    from ecs.core.models import Submission
    from ecs.core.workflow import (InitialReview, Resubmission, CategorizationReview, PaperSubmissionReview, 
        ChecklistReview, ExternalReview, ExternalReviewInvitation, VoteRecommendation, VoteRecommendationReview, B2VoteReview)
    from ecs.core.workflow import is_acknowledged, is_thesis, is_expedited, has_recommendation, has_accepted_recommendation, has_b2vote, needs_external_review
    
    statistical_review_checklist_blueprint = ChecklistBlueprint.objects.get(name='Statistik') 
    insurance_review_checklist_blueprint = ChecklistBlueprint.objects.get(name='Insurance Review')
    legal_and_patient_review_checklist_blueprint = ChecklistBlueprint.objects.get(name='Legal and Patient Review')
    boardmember_review_checklist_blueprint = ChecklistBlueprint.objects.get(name='Board Member Review')
    
    THESIS_REVIEW_GROUP = 'EC-Thesis Review Group'
    THESIS_EXECUTIVE_GROUP = 'EC-Thesis Executive Group'
    EXECUTIVE_GROUP = 'EC-Executive Board Group'
    PRESENTER_GROUP = 'Presenter'
    OFFICE_GROUP = 'EC-Office'
    BOARD_MEMBER_GROUP = 'EC-Board Member'
    EXTERNAL_REVIEW_GROUP = 'External Reviewer'
    INSURANCE_REVIEW_GROUP = 'EC-Insurance Reviewer'
    STATISTIC_REVIEW_GROUP = 'EC-Statistic Group'
    INTERNAL_REVIEW_GROUP = 'EC-Internal Review Group'
    
    setup_workflow_graph(Submission,
        auto_start=True,
        nodes={
            'start': Args(Generic, start=True, name="Start"),
            'generic_review': Args(Generic, name="Review Split"),
            'resubmission': Args(Resubmission, group=PRESENTER_GROUP),
            'initial_review': Args(InitialReview, group=OFFICE_GROUP),
            'b2_resubmission_review': Args(InitialReview, name="B2 Resubmission Review", group=INTERNAL_REVIEW_GROUP),
            'b2_vote_review': Args(B2VoteReview, group=OFFICE_GROUP),
            'categorization_review': Args(CategorizationReview, group=EXECUTIVE_GROUP),
            'initial_thesis_review': Args(InitialReview, name="Initial Thesis Review", group=THESIS_REVIEW_GROUP),
            'thesis_categorization_review': Args(CategorizationReview, name="Thesis Categorization Review", group=THESIS_EXECUTIVE_GROUP),
            'paper_submission_review': Args(PaperSubmissionReview, group=OFFICE_GROUP),
            'legal_and_patient_review': Args(ChecklistReview, data=legal_and_patient_review_checklist_blueprint, name=u"Legal and Patient Review", group=INTERNAL_REVIEW_GROUP),
            'insurance_review': Args(ChecklistReview, data=insurance_review_checklist_blueprint, name=u"Insurance Review", group=INSURANCE_REVIEW_GROUP),
            'statistical_review': Args(ChecklistReview, data=statistical_review_checklist_blueprint, name=u"Statistical Review", group=STATISTIC_REVIEW_GROUP),
            'board_member_review': Args(ChecklistReview, data=boardmember_review_checklist_blueprint, name=u"Board Member Review", group=BOARD_MEMBER_GROUP),
            'external_review': Args(ExternalReview, group=EXTERNAL_REVIEW_GROUP),
            'external_review_invitation': Args(ExternalReviewInvitation, group=OFFICE_GROUP),
            'thesis_vote_recommendation': Args(VoteRecommendation, group=THESIS_EXECUTIVE_GROUP),
            'vote_recommendation_review': Args(VoteRecommendationReview, group=EXECUTIVE_GROUP),
        },
        edges={
            ('start', 'initial_review'): Args(guard=is_thesis, negated=True),
            ('start', 'initial_thesis_review'): Args(guard=is_thesis),

            ('initial_review', 'resubmission'): Args(guard=is_acknowledged, negated=True),
            ('initial_review', 'categorization_review'): Args(guard=is_acknowledged),
            ('initial_review', 'paper_submission_review'): None,

            ('initial_thesis_review', 'resubmission'): Args(guard=is_acknowledged, negated=True),
            ('initial_thesis_review', 'thesis_categorization_review'): Args(guard=is_acknowledged),
            ('initial_thesis_review', 'paper_submission_review'): None,
            
            ('resubmission', 'start'): Args(guard=has_b2vote, negated=True),
            ('resubmission', 'b2_resubmission_review'): Args(guard=has_b2vote),
            ('b2_resubmission_review', 'b2_vote_review'): None,
            ('b2_vote_review', 'resubmission'): Args(guard=has_b2vote),

            ('thesis_categorization_review', 'thesis_vote_recommendation'): None,

            ('thesis_vote_recommendation', 'vote_recommendation_review'): Args(guard=has_recommendation),
            ('thesis_vote_recommendation', 'categorization_review'): Args(guard=has_recommendation, negated=True),

            #('vote_recommendation_review', 'END'): Args(guard=has_accepted_recommendation),
            ('vote_recommendation_review', 'categorization_review'): Args(guard=has_accepted_recommendation, negated=True),

            #('categorization_review', 'END'): Args(guard=is_expedited),
            ('categorization_review', 'generic_review'): Args(guard=is_expedited, negated=True),
            ('categorization_review', 'external_review_invitation'): Args(guard=needs_external_review),
            ('external_review_invitation', 'external_review'): None,
            ('external_review', 'external_review_invitation'): Args(deadline=True),

            ('generic_review', 'board_member_review'): None,
            ('generic_review', 'insurance_review'): None,
            ('generic_review', 'statistical_review'): None,
            ('generic_review', 'legal_and_patient_review'): None,
        }
    )
    

@bootstrap.register(depends_on=('ecs.integration.bootstrap.workflow_sync', 'ecs.core.bootstrap.auth_groups'))
def vote_workflow():
    from ecs.core.models import Vote
    from ecs.core.workflow import VoteFinalization, VoteReview, VoteSigning, VotePublication
    from ecs.core.workflow import is_executive_vote_review_required, is_final, is_b2upgrade

    setup_workflow_graph(Vote, 
        auto_start=True, 
        nodes={
            'start': Args(Generic, start=True, name="Start"),
            'review': Args(Generic, name="Review Split"),
            'b2upgrade': Args(Generic, name="B2 Upgrade", end=True),
            'executive_vote_finalization': Args(VoteReview, name="Executive Vote Finalization"),
            'executive_vote_review': Args(VoteReview, name="Executive Vote Review"),
            'internal_vote_review': Args(VoteReview, name="Internal Vote Review"),
            'office_vote_finalization': Args(VoteReview, name="Office Vote Finalization"),
            'office_vote_review': Args(VoteReview, name="Office Vote Review"),
            'final_office_vote_review': Args(VoteReview, name="Office Vote Review"),
            'vote_signing': Args(VoteSigning),
            'vote_publication': Args(VotePublication, end=True),
        }, 
        edges={
            ('start', 'review'): Args(guard=is_b2upgrade, negated=True),
            ('start', 'b2upgrade'): Args(guard=is_b2upgrade),
            ('review', 'executive_vote_finalization'): Args(guard=is_executive_vote_review_required),
            ('review', 'office_vote_finalization'): Args(guard=is_executive_vote_review_required, negated=True),
            ('executive_vote_finalization', 'office_vote_review'): None,
            ('office_vote_finalization', 'internal_vote_review'): None,

            ('office_vote_review', 'executive_vote_review'): Args(guard=is_final, negated=True),
            ('office_vote_review', 'vote_signing'): Args(guard=is_final),

            ('internal_vote_review', 'office_vote_finalization'): Args(guard=is_final, negated=True),
            ('internal_vote_review', 'executive_vote_review'): Args(guard=is_final),

            ('executive_vote_review', 'final_office_vote_review'): Args(guard=is_final, negated=True),
            ('executive_vote_review', 'vote_signing'): Args(guard=is_final),
            
            ('final_office_vote_review', 'executive_vote_review'): None,
            ('vote_signing', 'vote_publication'): None
        }
    )


@bootstrap.register()
def auth_groups():
    groups = (
        u'Presenter',
        u'Sponsor',
        u'Investigator',
        u'EC-Office',
        u'EC-Meeting Secretary',
        u'EC-Internal Review Group',
        u'EC-Executive Board Group',
        u'EC-Signing Group',
        u'EC-Statistic Group',
        u'EC-Notification Review Group',
        u'EC-Insurance Reviewer',
        u'EC-Thesis Review Group',
        u'EC-Thesis Executive Group',
        u'EC-Board Member',
        u'External Reviewer',
        u'userswitcher_target',
    )
    for group in groups:
        Group.objects.get_or_create(name=group)


@bootstrap.register()
def notification_types():
    types = (
        (u"Nebenwirkungsmeldung (SAE/SUSAR Bericht)", "ecs.core.forms.NotificationForm"),
        (u"Protokolländerung", "ecs.core.forms.NotificationForm"),
        (u"Zwischenbericht", "ecs.core.forms.ProgressReportNotificationForm"),
        (u"Abschlussbericht", "ecs.core.forms.CompletionReportNotificationForm"),
    )
    
    for name, form in types:
        NotificationType.objects.get_or_create(name=name, form=form)

@bootstrap.register()
def expedited_review_categories():
    for i in range(5):
        ExpeditedReviewCategory.objects.get_or_create(abbrev="ExRC%s" % i, name="Expedited Review Category #%s" % i)

@bootstrap.register()
def medical_categories():
    categories = (
        (u'Stats', u'Statistik'),
        (u'Pharma', u'Pharmakologie'), 
        (u'KlPh', u'Klinische Pharmakologie'),
        (u'Onko', u'Onkologie'),
        (u'Häm', u'Hämatologie'), 
        (u'Infektio', u'Infektiologie'),
        (u'Kardio', u'Kardiologie'),
        (u'Angio', u'Angiologie'),
        (u'Pulmo', u'Pulmologie'),
        (u'Endo', u'Endokrinologie'),
        (u'Nephro', u'Nephrologie'), 
        (u'Gastro', u'Gastroenterologie'),
        (u'Rheuma', u'Rheumatologie'),
        (u'Intensiv', u'Intensivmedizin'),
        (u'Chir', u'Chirugie'), 
        (u'plChir', u'Plastische Chirugie'),
        (u'HTChir', u'Herz-Thorax Chirugie'),
        (u'KiChir', u'Kinder Chirugie'),
        (u'NeuroChir', u'Neurochirurgie'),
        (u'Gyn', u'Gynäkologie'),
        (u'HNO', u'Hals-Nasen-Ohrenkrankheiten'),
        (u'Anästh', u'Anästhesie'),
        (u'Neuro', u'Neurologie'),
        (u'Psych', u'Psychatrie'),
        (u'Päd', u'Pädiatrie'),
        (u'Derma', u'Dermatologie'),
        (u'Radio', u'Radiologie'),
        (u'Transfus', u'Transfusionsmedizin'),
        (u'Ortho', u'Orthopädie'),
        (u'Uro', u'Urologie'), 
        (u'Notfall', u'Notfallmedizin'), 
        (u'PhysMed', u'Physikalische Medizin'),      
        (u'PsychAna', u'Psychoanalyse'),
        (u'Auge', u'Ophtalmologie'),
        (u'Nuklear', u'Nuklearmedizin'),
        (u'Labor', u'Labormedizin'),
        (u'Physiol', u'Physiologie'),
        (u'Anatomie', u'Anatomie'),
        (u'Zahn', u'Zahnheilkunde'),
        (u'ImmunPatho', u'Immunpathologie'),
        (u'Patho', u'Pathologie'),

        (u'Pfleger', u'Gesundheits und Krankenpfleger'),
        (u'Recht', u'Juristen'),
        (u'Pharmazie', u'Pharmazeuten'),
        (u'Patient', u'Patientenvertreter'), 
        (u'BehinOrg', u'Benhindertenorganisation'), 
        (u'Seel', u'Seelsorger'),
        (u'techSec', u'technischer Sicherheitsbeauftragter'),

        (u'LaborDia', u'medizinische und chemische Labordiagnostik'),
        (u'Psychol', u'Psychologie'), 
    )
    for shortname, longname in categories:
        medcat, created = MedicalCategory.objects.get_or_create(abbrev=shortname)
        medcat.name = longname
        medcat.save()

@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups',))
def auth_user_developers():
    ''' Developer Account Creation '''
    developers = (
        ('wuxxin', u'Felix', u'Erkinger', u'felix@erkinger.at'),
        ('mvw', 'Marc', 'van Woerkom', 'marc.vanwoerkom@googlemail.com'),
        ('emulbreh', u'Johannes', u'Dollinger', 'emulbreh@googlemail.com'),
        ('natano', u'Martin', u'Natano', 'natano@natano.net'),
        ('amir', u'amir', u'hassan', 'amir@viel-zu.org'),
        ('scripty', u'Ludwig', u'Hammel', 'ludwig.hammel@gmail.com'),
        ('froema', u'Markus', u'Froehlich', 'froema@ep3.at'),
    )
    
    for dev in developers:
        user, created = User.objects.get_or_create(username=dev[0])
        user.first_name = dev[1]
        user.last_name = dev[2]
        user.email = dev[3]
        user.set_password(dev[4])
        user.is_staff = True
        user.groups.add(Group.objects.get(name="Presenter"))
        user.save()
        profile = user.get_profile()
        profile.approved_by_office = True
        profile.save()
        
        

@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups','ecs.core.bootstrap.medical_categories'))
def auth_user_testusers():
    ''' Test User Creation, target to userswitcher'''
    testusers = (
        (u'Presenter', u'Presenter',{'approved_by_office': True}),
        (u'Sponsor', u'Sponsor', {'approved_by_office': True}),
        (u'Investigtor', u'Investigator', {'approved_by_office': True}),
        (u'Office', u'EC-Office', {'internal': True, 'approved_by_office': True}),
        (u'Meeting Secretary', u'EC-Meeting Secretary',
            {'internal': True, 'approved_by_office': True}),
        (u'Internal Rev', u'EC-Internal Review Group',
            {'internal': True, 'approved_by_office': True}),
        (u'Executive', u'EC-Executive Board Group',             
            {'internal': True, 'executive_board_member': True, 'approved_by_office': True}),
        (u'Signing', u'EC-Signing Group',                       
            {'internal': True, 'approved_by_office': True}),
        (u'Statistic Rev', u'EC-Statistic Group',
            {'internal': True, 'approved_by_office': True}),
        (u'Notification Rev', u'EC-Notification Review Group',
            {'internal': True, 'approved_by_office': True}),
        (u'Insurance Rev', u'EC-Insurance Reviewer',            
            {'internal': True, 'approved_by_office': True}),
        (u'Thesis Rev', u'EC-Thesis Review Group',              
            {'internal': True, 'thesis_review': True, 'approved_by_office': True}),
        (u'External Reviewer', u'External Reviewer',            
            {'external_review': True, 'approved_by_office': True}),
    )
        
    boardtestusers = (
         (u'B.Member 1 (KlPh)', ('KlPh',)),
         (u'B.Member 2 (KlPh, Onko)', ('KlPh','Onko')),
         (u'B.Member 3 (Onko)', ('Onko',)),
         (u'B.Member 4 (Infektio)', ('Infektio',)),
         (u'B.Member 5 (Kardio)', ('Kardio',)),
         (u'B.Member 6 (Päd)', ('Päd',)), 
    )
    
    for testuser, testgroup, flags in testusers:
        for number in range(1,4):
            user, created = User.objects.get_or_create(username=" ".join((testuser,str(number))))
            user.groups.add(Group.objects.get(name=testgroup))
            user.groups.add(Group.objects.get(name="userswitcher_target"))

            profile = user.get_profile()
            for flagname, flagvalue in flags.items():
                setattr(profile, flagname, flagvalue)
            profile.save()
    
    for testuser, medcategories in boardtestusers:
        user, created = User.objects.get_or_create(username=testuser)
        user.groups.add(Group.objects.get(name='EC-Board Member'))
        user.groups.add(Group.objects.get(name="userswitcher_target"))

        profile = user.get_profile()
        profile.board_member = True
        profile.approved_by_office = True
        profile.save()

        for medcategory in medcategories:
            m= MedicalCategory.objects.get(abbrev=medcategory)
            m.users.add(user)

@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups',))
def auth_ec_staff_users():
    staff_users = ()
    
    for blueprint in blueprints:
        #FIXME: we need a unique constraint on name for this to be idempotent
        ChecklistBlueprint.objects.get_or_create(name=blueprint)

@bootstrap.register(depends_on=('ecs.core.bootstrap.checklist_blueprints',))
def checklist_questions():
    questions = {
        u'Statistik': (
            u'1. Ist das Studienziel ausreichend definiert?',
            u'2. Ist das Design der Studie geeignet, das Studienziel zu erreichen?',
            u'3. Ist die Studienpopulation ausreichend definiert?',
            u'4. Sind die Zielvariablen geeignet definiert?',
            u'5. Ist die statistische Analyse beschrieben, und ist sie ad\u00e4quat?',
            u'6. Ist die Gr\u00f6\u00dfe der Stichprobe ausreichend begr\u00fcndet?',
        ),
        u'Legal and Patient Review': (u"42 ?",),
        u'Insurance Review': (u"42 ?",),
        u'Board Member Review': (u"42 ?",),
    }

    for bp_name in questions.keys():
        blueprint = ChecklistBlueprint.objects.get(name=bp_name)
        print blueprint
        #FIXME: there is no unique constraint, so this is not idempotent
        for q in questions[bp_name]:
            cq, created = ChecklistQuestion.objects.get_or_create(text=q, blueprint=blueprint)

@bootstrap.register(depends_on=('ecs.core.bootstrap.checklist_questions', 'ecs.core.bootstrap.medical_categories', 'ecs.core.bootstrap.ethics_commissions', 'ecs.core.bootstrap.auth_user_testusers', 'ecs.documents.bootstrap.document_types',))
@sudo(lambda: User.objects.get(username='Presenter 1'))
def testsubmission():
    with sudo(): # XXX: this fixes a visibility problem, as presenters are currently not allowed to see their own submissions
        if Submission.objects.filter(ec_number='4321').exists():
            return
    submission = Submission.objects.create(ec_number='4321')
    submission.medical_categories.add(MedicalCategory.objects.get(abbrev='Päd'))
    
    submission_form_data = {
        'invoice_uid': u'',
        'study_plan_abort_crit': u'Peto',
        'medtech_product_name': u'',
        'study_plan_statistics_implementation': u'Mag. rer.soc.oec. Ulrike P\u00f6tschger / Statistikerin',
        'sponsor_fax': u'+43 1 4017070',
        'substance_p_c_t_final_report': True,
        'project_type_basic_research': False,
        'medtech_ce_symbol': False,
        'study_plan_alpha': u'0.05',
        'project_type_reg_drug': False,
        'study_plan_secondary_objectives': None,
        'eudract_number': u'2006-001489-17',
        'study_plan_dropout_ratio': u'0',
        'german_protected_subjects_info': u'bla bla bla',
        'project_type_genetic_study': False,
        'study_plan_blind': None,
        'study_plan_misc': None,
        'project_type_retrospective': False,
        'german_preclinical_results': u'bla bla bla',
        'study_plan_biometric_planning': u'Mag. rer.soc.oec. Ulrike P\u00f6tschger / Statistikerin',
        'invoice_uid_verified_level2': None,
        'study_plan_placebo': False,
        'submitter_jobtitle': u'OA am St. Anna Kinderspital',
        'project_type_medical_device': False,
        'german_aftercare_info': u'bla bla bla',
        'german_recruitment_info': u'bla bla bla',
        'study_plan_factorized': False,
        'invoice_uid_verified_level1': None,
        'project_type_medical_device_performance_evaluation': False,
        'german_dataprotection_info': u'bla bla bla',
        'german_concurrent_study_info': u'bla bla bla',
        'study_plan_planned_statalgorithm': u'log rank test',
        'submission': submission,
        'medtech_reference_substance': u'',
        'study_plan_statalgorithm': u'Lachin and Foulkes',
        'subject_duration_active': u'12 months',
        'submitter_is_coordinator': True,
        'sponsor_name': u'CCRI',
        'sponsor_email': u'helmut.gadner@stanna.at',
        'subject_duration': u'48 months',
        'pharma_reference_substance': u'1) R1 Randomisierung BUMEL - MAT/SCR',
        'project_type_questionnaire': False,
        'submitter_is_main_investigator': False,
        'insurance_phone': u'50125',
        'study_plan_population_intention_to_treat': False,
        'submitter_contact_last_name': u'Ladenstein',
        'submitter_contact_title': u'Univ. Doz. Dr.',
        'submitter_contact_gender': 'f',
        'submitter_contact_first_name': u'Ruth',
        'submitter_is_authorized_by_sponsor': False,
        'medtech_manufacturer': u'',
        'subject_planned_total_duration': u'8 months',
        'project_type_medical_device_with_ce': False,
        'submitter_is_sponsor': False,
        'german_summary': u'Bei diesem Projekt handelt es sich um ein sowieso bla blu',
        'insurance_contract_number': u'WF-07218230-8',
        'study_plan_power': u'0.80',
        'study_plan_multiple_test_correction_algorithm': u'Keines',
        'sponsor_phone': u'+43 1 40170',
        'subject_maxage': 21,
        'subject_noncompetents': True,
        'date_of_receipt': None,
        'project_type_medical_device_without_ce': False,
        'invoice_phone': u'',
        'german_risks_info': u'bla bla bla',
        'german_ethical_info': u'bla bla bla',
        'specialism': u'P\u00e4diatrische Onkologie / Immunologie',
        'study_plan_population_per_protocol': False,
        'medtech_certified_for_other_indications': False,
        'study_plan_parallelgroups': False,
        'german_payment_info': u'bla bla bla',
        'study_plan_controlled': False,
        'study_plan_dataprotection_anonalgoritm': u'Electronically generated unique patient number within SIOPEN-R-Net',
        'additional_therapy_info': u'long blabla',
        'german_inclusion_exclusion_crit': u'bla bla bla',
        'medtech_technical_safety_regulations': u'',
        'study_plan_pilot_project': False,
        'study_plan_number_of_groups': None,
        'insurance_name': u'Z\u00fcrich Veresicherungs-Aktiengesellschaft',
        'study_plan_null_hypothesis': None,
        'clinical_phase': u'III',
        'substance_preexisting_clinical_tries': True,
        'substance_p_c_t_phase': u'III',
        'subject_males': True,
        'substance_p_c_t_period': u'Anti-GD2-Phase I: 1989-1992, Phase III 2002',
        'german_benefits_info': u'bla bla bla',
        'german_abort_info': u'bla bla bla',
        'insurance_address_1': u'Schwarzenbergplatz 15',
        'german_additional_info': u'bla bla bla',
        'study_plan_primary_objectives': None,
        'study_plan_dataprotection_reason': u'',
        'medtech_certified_for_exact_indications': False,
        'sponsor_city': u'Wien',
        'medtech_manual_included': False,
        'sponsor_agrees_to_publishing': True,
        'study_plan_alternative_hypothesis': None,
        'medtech_checked_product': u'',
        'study_plan_sample_frequency': None,
        'study_plan_dataquality_checking': u'National coordinators cross check in local audits patient file data with electronic data. In addition the RDE system holds electronic plausibility controls.',
        'project_type_non_reg_drug': False,
        'german_relationship_info': u'bla bla bla',
        'project_title': u'High Risk Neuroblastoma Study 1 of SIOP-Europe (SIOPEN)',
        'invoice_fax': u'',
        'sponsor_zip_code': u'1090',
        'insurance_validity': u'01.10.2005 bis 01.10.2006',
        'already_voted': True,
        'subject_duration_controls': u'36 months',
        'study_plan_dataprotection_dvr': u'',
        'german_sideeffects_info': u'bla bla bla',
        'subject_females': True,
        'pharma_checked_substance': u'1) R1 Randomisierung CEM - MAT/SCR',
        'project_type_misc': None,
        'invoice_city': u'',
        'german_financing_info': u'bla bla bla',
        'project_type_register': False,
        'german_dataaccess_info': u'bla bla bla',
        'project_type_biobank': False,
        'study_plan_observer_blinded': False,
        'substance_p_c_t_application_type': u'IV in children',
        'invoice_zip_code': u'',
        'project_type_reg_drug_within_indication': False,
        'invoice_email': u'',
        'study_plan_datamanagement': u'Date entry and management through the SIOPEN-R-Net platform including the RDE system',
        'german_primary_hypothesis': u'bla bla bla',
        'subject_childbearing': True,
        'study_plan_stratification': None,
        'project_type_reg_drug_not_within_indication': False,
        'project_type_medical_method': False,
        'project_type_education_context': None,
        'invoice_address1': u'',
        'invoice_address2': u'',
        'study_plan_equivalence_testing': False,
        'subject_count': 175,
        'substance_p_c_t_gcp_rules': True,
        'subject_minage': 0,
        'study_plan_blind': 0,
        'study_plan_randomized': False,
        'study_plan_cross_over': False,
        'german_consent_info': u'bla bla bla',
        'medtech_departure_from_regulations': u'',
        'german_project_title': u'Riskikoreiche Neuroblastom Studie 1 von SIOP-Europe (SIOPEN)',
        'submitter_organisation': u'St. Anna Kinderspital',
        'sponsor_address1': u'Kinderspitalg. 6',
        'invoice_name': u'',
        'sponsor_address2': u'',
        'german_statistical_info': u'bla bla bla',
    }
    
    patienteninformation_filename = os.path.join(os.path.dirname(__file__), 'patienteninformation.pdf')
    with open(patienteninformation_filename, 'rb') as patienteninformation:
        doctype = DocumentType.objects.get(identifier='patientinformation')
        doc = Document.objects.create_from_buffer(patienteninformation.read(), version='1', doctype=doctype, date=datetime.now())
        doc.save()

    submission_form = SubmissionForm.objects.create(**submission_form_data)
    submission_form.substance_p_c_t_countries.add(Country.objects.get(iso='AT'))
    submission_form.substance_p_c_t_countries.add(Country.objects.get(iso='DE'))
    submission_form.substance_p_c_t_countries.add(Country.objects.get(iso='US'))

    doc.parent_object = submission_form
    doc.save()
    
    Investigator.objects.create(
        contact_last_name=u'Univ. Doz. Dr. Ruth Ladenstein',
        submission_form=submission_form,
        subject_count=1,
        organisation=u'Kinderspital St. Anna',
        ethics_commission=EthicsCommission.objects.get(name=u'Ethikkomission der Medizinischen Universit\u00e4t Wien')
    )
    
    checklist, created = Checklist.objects.get_or_create(
        submission=submission,
        blueprint=ChecklistBlueprint.objects.get(name=u'Statistik'),
        defaults={'user': User.objects.get(username='root')}
    )
    
    for q in ChecklistQuestion.objects.all():
        ca = ChecklistAnswer.objects.get_or_create(
            question=q,
            checklist=checklist,
            defaults={
                'answer': random.choice((True, False, None,))
            }
        )




