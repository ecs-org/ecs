# -*- coding: utf-8 -*-
import os, random
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import CommandError
from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.core.files import File

from ecs import bootstrap
from ecs.core.models import (ExpeditedReviewCategory, Submission, MedicalCategory, EthicsCommission, ChecklistBlueprint, ChecklistQuestion,
    Investigator, SubmissionForm, Checklist, ChecklistAnswer)
from ecs.utils.countries.models import Country
from ecs.utils import Args
from ecs.users.utils import sudo
from ecs.documents.models import Document, DocumentType
from ecs.workflow.patterns import Generic
from ecs.integration.utils import setup_workflow_graph
from ecs.users.utils import get_or_create_user


# We use this helper function for marking task names as translatable, they are
# getting translated later.
_ = lambda s: s

@bootstrap.register()
def default_site():
    # default_site is needed for dbtemplates
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
    from ecs.core.workflow import (InitialReview, Resubmission, CategorizationReview, PaperSubmissionReview, AdditionalReviewSplit, AdditionalChecklistReview,
        ChecklistReview, ExternalChecklistReview, VoteRecommendation, VoteRecommendationReview, B2VoteReview)
    from ecs.core.workflow import (is_acknowledged, is_thesis, is_expedited, has_recommendation, has_accepted_recommendation, has_b2vote, needs_external_review,
        needs_insurance_review, needs_gcp_review, needs_boardmember_review)
    
    statistical_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='statistic_review')
    insurance_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='insurance_review')
    legal_and_patient_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='legal_review')
    boardmember_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='boardmember_review')
    external_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='external_review')
    additional_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='additional_review')
    gcp_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='gcp_review')
    
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
    GCP_REVIEW_GROUP = 'GCP Review Group'
    
    setup_workflow_graph(Submission,
        auto_start=True,
        nodes={
            'start': Args(Generic, start=True, name=_("Start")),
            'generic_review': Args(Generic, name=_("Review Split")),
            'resubmission': Args(Resubmission, name=_("Resubmission")),
            'initial_review': Args(InitialReview, group=OFFICE_GROUP, name=_("Initial Review")),
            'b2_resubmission_review': Args(InitialReview, name=_("B2 Resubmission Review"), group=INTERNAL_REVIEW_GROUP),
            'b2_vote_review': Args(B2VoteReview, group=OFFICE_GROUP, name=_("B2 Vote Review")),
            'categorization_review': Args(CategorizationReview, group=EXECUTIVE_GROUP, name=_("Categorization Review")),
            'additional_review_split': Args(AdditionalReviewSplit, name=_("Additional Review Split")),
            'additional_review': Args(AdditionalChecklistReview, data=additional_review_checklist_blueprint, name=_("Additional Checklist Review")),
            'initial_thesis_review': Args(InitialReview, name=_("Initial Thesis Review"), group=THESIS_REVIEW_GROUP),
            'thesis_categorization_review': Args(CategorizationReview, name=_("Thesis Categorization Review"), group=THESIS_EXECUTIVE_GROUP),
            'paper_submission_review': Args(PaperSubmissionReview, group=OFFICE_GROUP, name=_("Paper Submission Review")),
            'legal_and_patient_review': Args(ChecklistReview, data=legal_and_patient_review_checklist_blueprint, name=_("Legal and Patient Review"), group=INTERNAL_REVIEW_GROUP),
            'insurance_review': Args(ChecklistReview, data=insurance_review_checklist_blueprint, name=_("Insurance Review"), group=INSURANCE_REVIEW_GROUP),
            'statistical_review': Args(ChecklistReview, data=statistical_review_checklist_blueprint, name=_("Statistical Review"), group=STATISTIC_REVIEW_GROUP),
            'board_member_review': Args(ChecklistReview, data=boardmember_review_checklist_blueprint, name=_("Board Member Review"), group=BOARD_MEMBER_GROUP),
            'external_review': Args(ExternalChecklistReview, data=external_review_checklist_blueprint, name=_("External Review"), group=EXTERNAL_REVIEW_GROUP),
            'gcp_review': Args(ChecklistReview, data=gcp_review_checklist_blueprint, name=_("GCP Review"), group=GCP_REVIEW_GROUP),
            'thesis_vote_recommendation': Args(VoteRecommendation, group=THESIS_EXECUTIVE_GROUP, name=_("Vote Recommendation")),
            'vote_recommendation_review': Args(VoteRecommendationReview, group=EXECUTIVE_GROUP, name=_("Vote Recommendation Review")),
        },
        edges={
            ('start', 'initial_review'): Args(guard=is_thesis, negated=True),
            ('start', 'initial_thesis_review'): Args(guard=is_thesis),

            ('initial_review', 'resubmission'): Args(guard=is_acknowledged, negated=True),
            ('initial_review', 'categorization_review'): Args(guard=is_acknowledged),
            ('initial_review', 'paper_submission_review'): Args(guard=is_acknowledged),

            ('initial_thesis_review', 'resubmission'): Args(guard=is_acknowledged, negated=True),
            ('initial_thesis_review', 'thesis_categorization_review'): Args(guard=is_acknowledged),
            ('initial_thesis_review', 'paper_submission_review'): Args(guard=is_acknowledged),
            
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
            ('categorization_review', 'external_review'): Args(guard=needs_external_review),
            ('categorization_review', 'additional_review_split'): None,
            
            ('additional_review_split', 'additional_review'): None,

            ('generic_review', 'board_member_review'): Args(guard=needs_boardmember_review),
            ('generic_review', 'insurance_review'): Args(guard=needs_insurance_review),
            ('generic_review', 'statistical_review'): None,
            ('generic_review', 'legal_and_patient_review'): None,
            ('generic_review', 'gcp_review'): Args(guard=needs_gcp_review),
        }
    )
    

@bootstrap.register(depends_on=('ecs.integration.bootstrap.workflow_sync', 'ecs.core.bootstrap.auth_groups'))
def vote_workflow():
    from ecs.core.models import Vote
    from ecs.core.workflow import VoteFinalization, VoteReview, VoteSigning, VotePublication
    from ecs.core.workflow import is_executive_vote_review_required, is_final, is_b2upgrade
    
    EXECUTIVE_GROUP = 'EC-Executive Board Group'
    OFFICE_GROUP = 'EC-Office'
    INTERNAL_REVIEW_GROUP = 'EC-Internal Review Group'
    SIGNING_GROUP = 'EC-Signing Group'

    setup_workflow_graph(Vote, 
        auto_start=True, 
        nodes={
            'start': Args(Generic, start=True, name=_("Start")),
            'review': Args(Generic, name=_("Review Split")),
            'b2upgrade': Args(Generic, name=_("B2 Upgrade"), end=True),
            'executive_vote_finalization': Args(VoteReview, name=_("Executive Vote Finalization"), group=EXECUTIVE_GROUP),
            'executive_vote_review': Args(VoteReview, name=_("Executive Vote Review"), group=EXECUTIVE_GROUP),
            'internal_vote_review': Args(VoteReview, name=_("Internal Vote Review"), group=INTERNAL_REVIEW_GROUP),
            'office_vote_finalization': Args(VoteReview, name=_("Office Vote Finalization"), group=OFFICE_GROUP),
            'office_vote_review': Args(VoteReview, name=_("Office Vote Review"), group=OFFICE_GROUP),
            'final_office_vote_review': Args(VoteReview, name=_("Office Vote Review"), group=OFFICE_GROUP),
            'vote_signing': Args(VoteSigning, group=SIGNING_GROUP, name=_("Vote Signing")),
            'vote_publication': Args(VotePublication, end=True, group=OFFICE_GROUP, name=_("Vote Publication")),
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
        u'GCP Review Group',
    )
    for group in groups:
        Group.objects.get_or_create(name=group)


@bootstrap.register()
def expedited_review_categories():
    categories = (
        (u'KlPh', u'Klinische Pharmakologie'),
        (u'Stats', u'Statistik'),
        (u'Labor', u'Labormedizin'),
        (u'Recht', u'Juristen'),
        (u'Radio', u'Radiologie'),
        (u'Anästh', u'Anästhesie'),
        (u'Psychol', u'Psychologie'),
        (u'Patho', u'Pathologie'),
        (u'Zahn', u'Zahnheilkunde'),
        )
    for abbrev, name in categories:
        ExpeditedReviewCategory.objects.get_or_create(abbrev=abbrev, name=name)


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
        
        (u'Virologie', u'Virologie'),
        (u'Tropen', u'Tropen'),
        (u'Ernährung', u'Ernährung'),
        (u'Apotheke', u'Apotheke'),
    )
    for shortname, longname in categories:
        medcat, created = MedicalCategory.objects.get_or_create(abbrev=shortname)
        medcat.name = longname
        medcat.save()

@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups',))
def auth_user_developers():
    ''' Developer Account Creation '''
    try:
        from ecs.core.bootstrap_settings import developers
    except ImportError:
        # first, Last, email, password, is_supeuser
        developers = ((u'John', u'Doe', u'developer@example.org', 'changeme', False, 'f'),)
        
    for first, last, email, password, is_superuser, gender in developers:
        user, created = get_or_create_user(email)
        user.first_name = first
        user.last_name = last
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = is_superuser
        user.groups.add(Group.objects.get(name="Presenter"))
        user.save()
        profile = user.get_profile()
        profile.approved_by_office = True
        profile.help_writer = True
        profile.forward_messages_after_minutes = 360
        profile.gender = gender
        profile.save()


@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups', 
    'ecs.core.bootstrap.expedited_review_categories', 'ecs.core.bootstrap.medical_categories'))
def auth_user_sentryuser():
        user, created = get_or_create_user('sentry@example.org')
        user.groups.add(Group.objects.get(name="Presenter"))
        user.groups.add(Group.objects.get(name="userswitcher_target"))
        user.is_staff = True
        user.is_superuser = True
        user.save()
        flags = {'approved_by_office': True}
        profile = user.get_profile()
        for flagname, flagvalue in flags.items():
            setattr(profile, flagname, flagvalue)
        profile.save()


@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups', 
    'ecs.core.bootstrap.expedited_review_categories', 'ecs.core.bootstrap.medical_categories'))
def auth_user_testusers():
    ''' Test User Creation, target to userswitcher'''
    testusers = (
        ('presenter', u'Presenter',{'approved_by_office': True}),
        ('sponsor', u'Sponsor', {'approved_by_office': True}),
        ('investigator', u'Investigator', {'approved_by_office': True}),
        ('office', u'EC-Office', {'internal': True, 'approved_by_office': True}),
        ('internal.rev', u'EC-Internal Review Group',
            {'internal': True, 'approved_by_office': True}),
        ('executive', u'EC-Executive Board Group',
            {'internal': True, 'executive_board_member': True),
        ('thesis.executive', u'EC-Thesis Executive Group',
            {'internal': True, 'executive_board_member': True),
        ('signing', u'EC-Signing Group',
            {'internal': True, 'approved_by_office': True}),
        ('statistic.rev', u'EC-Statistic Group',
            {'internal': True, 'approved_by_office': True}),
        ('notification.rev', u'EC-Notification Review Group',
            {'internal': True, 'approved_by_office': True}),
        ('insurance.rev', u'EC-Insurance Reviewer',
            {'internal': False, 'approved_by_office': True),
        ('thesis.rev', u'EC-Thesis Review Group',
            {'internal': False, 'thesis_review': True),
        ('external.reviewer', u'External Reviewer',
            {'external_review': True, 'approved_by_office': True}),
        ('gcp.reviewer', u'GCP Review Group',
            {'internal': True, 'approved_by_office': True}),
    )

    boardtestusers = (
         ('b.member1.klph', ('KlPh',)),
         ('b.member2.klph.onko', ('KlPh','Onko')),
         ('b.member3.onko', ('Onko',)),
         ('b.member4.infektio', ('Infektio',)),
         ('b.member5.kardio', ('Kardio',)),
         ('b.member6.paed', ('Päd',)), 
    )

    
    for testuser, testgroup, flags in testusers:
        for number in range(1,4):
            user, created = get_or_create_user('{0}{1}@example.org'.format(testuser, number))
            user.groups.add(Group.objects.get(name=testgroup))
            user.groups.add(Group.objects.get(name="userswitcher_target"))

            profile = user.get_profile()
            for flagname, flagvalue in flags.items():
                setattr(profile, flagname, flagvalue)
            if number == 3:
                # XXX set every third userswitcher user to be included in help_writer group
                profile.help_writer = True
                
            profile.save()

    
    for testuser, medcategories in boardtestusers:
        user, created = get_or_create_user('{0}@example.org'.format(testuser))
        user.groups.add(Group.objects.get(name='EC-Board Member'))
        user.groups.add(Group.objects.get(name="userswitcher_target"))

        profile = user.get_profile()
        profile.board_member = True
        profile.approved_by_office = True
        profile.save()

        for medcategory in medcategories:
            m= MedicalCategory.objects.get(abbrev=medcategory)
            m.users.add(user)
            try:
                e= ExpeditedReviewCategory.objects.get(abbrev=medcategory)
                e.users.add(user)
            except ObjectDoesNotExist:
                pass

@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups',))
def auth_ec_staff_users():
    try:
        from ecs.core.bootstrap_settings import staff_users
    except ImportError:
        staff_users = ()
    
    for blueprint in blueprints:
        b, _ = ChecklistBlueprint.objects.get_or_create(slug=blueprint['slug'])
        changed = False
        for name, value in blueprint.items():
            if getattr(b, name) != value:
                setattr(b, name, value)
                changed = True
        if changed:
            b.save()

@bootstrap.register(depends_on=('ecs.core.bootstrap.checklist_blueprints',))
def checklist_questions():
    questions = {
        u'statistic_review': [
            (u'1. Ist das Studienziel ausreichend definiert?',u''),
            (u'2. Ist das Design der Studie geeignet, das Studienziel zu erreichen?',u''),
            (u'3. Ist die Studienpopulation ausreichend definiert?',u''),
            (u'4. Sind die Zielvariablen geeignet definiert?',u''),
            (u'5. Ist die statistische Analyse beschrieben, und ist sie adäquat?',u''),
            (u'6. Ist die Größe der Stichprobe ausreichend begründet?',u''),
        ],
        u'legal_review': [
                          (u" 1. Anrede: entspricht?",u''),
                          (u" 2. Hinweis auf Freiwilligkeit: entspricht?",u''),
                          (u" 3. Hinweis auf jederzeitigen Abbruch: entspricht?",u''),
                          (u" 4. Schwangerschaftspassus: entspricht?",u''),
                          (u" 5. Versicherungspassus: entspricht?",u''),
                          (u" 6. Name und Erreichbarkeit des Prüfarztes: entspricht?",u''),
                          (u" 7. Hinweis auf Patientenanwaltschaft: entspricht?",u''),
                          (u" 8. Vermeidung von Fremdwörtern: entspricht?",u''),
                          (u" 9. Rechtschreibung und Grammatik: entspricht?",u''),
                          (u"10. Die Patienteninformation entspricht in allen anderen Punkten den Anforderungen?",u''),
                          ],
        u'insurance_review': [(u" 1. Sind die Angaben zu Versicherung vollständig und adäquat?",u''),],
        u'external_review': [
            (u'1a. Ist die Ausarbeitung des Projektes hinreichend um es begutachten zu können?',u''),
            (u'''1b. Ist das Projekt vollständig (inkl. Angaben über Nebenwirkungen etc.)?''',
                u'Bitte beurteilen Sie in diesem Zusammenhang auch die Vollständigkeit und Richtigkeit der in der Kurzfassung enthaltenen Aufstellung der studienbezogenen Maßnahmen!'),
            (u'2. Ist die Fragestellung des Projektes relevant/wenig relevant/bereits bearbeitet/irrelevant?',u''),
            (u'3. Ist die angewandte Methodik geeignet, die Fragestellung zu beantworten?',u''),
            (u'3a. Findet sich im Protokoll eine Begründung der gewählten Fallzahl und eine Angabe über die geplante statistische Auswertung?',u''),
            (u'4a. Werden den Patienten/Probanden durch das Projekt besondere Risken zugemutet?',
                    u'''- durch eine neue Substanz mit hoher Nebenwirkungsrate
                    - durch Vorenthalten einer wirksamen Therapie
                    - durch radioaktive Isotope
                    - durch eine spezielle Dosierung von Medikamenten'''),
            (u'4b. Stehen diese Risken Ihrer Meinung nach in einem akzeptablen Verhältnis zum zu erwartenden Nutzen der Studie?',u''),
            (u'5a. Werden dem Patienten/Probanden durch die für die Studie notwendigen Untersuchungen besondere Belastungen bzw. Risken zugemutet?',u''),
            (u'5b. Stehen diese Belastungen in einem akzeptablen Verhältnis zum zu erwartenden Nutzen der Studie ?',u''),
            (u'6. Liegt ein Patienteninformationsblatt bei? Ist dieses ausreichend und verständlich?',u''),  
        ],
        u'additional_review': [(u"42 ?",u''),],
        u'gcp_review': [
            (u' 1. Sind die Allgemeinen Informationen ausreichend und korrekt angegeben?',u''),
            (u' 2. Sind die Hintergrund Informationen ausreichend und korrekt angegeben?',u''),
            (u' 3. Ist das Studienziel und der Studienzweck detailiert beschrieben?',u''),
            (u' 4. Ist das Studiendesign ausreichend dargelegt? (Endpunkte, Studienphase, Bias-Vermeidung, Prüfpräparat, Labelling, Dauer, Beendigung, Accountability, Randomisierung, Source Daten)',u''),
            (u' 5. Sind Patientenauswahl und -Austritts bzw. Abbruchkriterien ausreichend definiert? (Ein-/Ausschluss, Abbruch, Datenerhebung, follow up, Ersatz)',u''),
            (u' 6. Ist die Behandlung der Studienteilnehmer, samt erlaubter/nicht erlaubter Medikation und Überprüfungsverfahren ausreichend definiert?',u''),
            (u' 7. Sind die Efficacy Parameter sowie Methoden, zeitliche Planung und Erfassung & Analyse d. Efficacy Parameter ausreichend definiert?',u''),
            (u' 8. Ist Safety und Safety Reporting ausreichend definiert, und adäquat?',u''),
            (u' 9. Sind die Angaben zur statistischen Datenerhebung, -Auswertung, -Methoden ausreichend und adäquat?',u''),
            (u'10. Ist die Qualitätskontrolle und Qualitätssicherung ausreichend beschrieben und sind diese Angaben adäquat?',u''),
            (u'11. Ethik?',u''),
            (u'12. Sind Angaben zu Datenerhebung, Dokumentation und Verarbeitung ausreichend definiert und sind diese adäquat?',u''),
            (u'13. Sind Angaben zu Finanzierung und Versicherung ausreichend definiert und sind diese adäquat?',u''),
            (u'14. Sind Angaben zur Regelung bzgl Publikation ausreichend definiert?',u''),
            (u'15. Anhang, wenn zutreffend?',u''),
        ],
        u'boardmember_review': [
                                (u" 1. Ist das Antragsformular korrekt und vollständig ausgefüllt?",u''),
                                (u" 2. Entspricht das Protokoll /der Prüfplan formal und inhaltlich den Richtlinien der „Guten wissenschaftlichen Praxis“ der MedUni Wien?",u''),
                                (u" 3. Entspricht/ entsprechen die Patienten/Probandeninformation(en) den formalen, inhaltlichen und sprachlichen Anforderungen?",u''),
                                ],
        u'expedited_review': [
                                (u" 1. Ist das Antragsformular korrekt und vollständig ausgefüllt?",u''),
                                (u" 2. Entspricht das Protokoll /der Prüfplan formal und inhaltlich den Richtlinien der „Guten wissenschaftlichen Praxis“ der MedUni Wien?",u''),
                                (u" 3. Entspricht/ entsprechen die Patienten/Probandeninformation(en) den formalen, inhaltlichen und sprachlichen Anforderungen?",u''),
                                ],
    }

    for slug in questions.keys():
        blueprint = ChecklistBlueprint.objects.get(slug=slug)
        for qdtup in questions[slug]:
            cq, created = ChecklistQuestion.objects.get_or_create(text=qdtup[0], blueprint=blueprint, description=qdtup[1])

@bootstrap.register(depends_on=('ecs.core.bootstrap.checklist_questions', 'ecs.core.bootstrap.medical_categories', 'ecs.core.bootstrap.ethics_commissions', 'ecs.core.bootstrap.auth_user_testusers', 'ecs.documents.bootstrap.document_types',))
def testsubmission():
    # FIXME disabled testsubmission for now, because it is not valid, and produces more followup errors than usefull testing
    return

    if Submission.objects.filter(ec_number=20104321):
        return
    submission, created = Submission.objects.get_or_create(ec_number=20104321)
    submission.medical_categories.add(MedicalCategory.objects.get(abbrev=u'Päd'))
    
    try:
        from ecs.core.bootstrap_settings import test_submission_form
    except ImportError:
        test_submission_form = {
            'acknowledged': False,
            'additional_therapy_info': u'',
            'already_voted': False,
            'clinical_phase': u'Neu',
            'created_at': datetime(2010, 11, 24, 18, 19, 13, 842468),
            'date_of_receipt': None,
            'eudract_number': u'',
            'external_reviewer_suggestions': u'',
            'german_abort_info': u'blabla',
            'german_additional_info': u'',
            'german_aftercare_info': u'blabla',
            'german_benefits_info': u'blabla',
            'german_concurrent_study_info': u'blabla',
            'german_consent_info': u'blabla',
            'german_dataaccess_info': u'',
            'german_dataprotection_info': u'',
            'german_ethical_info': u'blabla',
            'german_financing_info': u'',
            'german_inclusion_exclusion_crit': u'blabla',
            'german_payment_info': u'blabla',
            'german_preclinical_results': u'blabla',
            'german_primary_hypothesis': u'blabla',
            'german_project_title': u'Implantierung von Telefonen ins Ohr',
            'german_protected_subjects_info': u'blabla',
            'german_recruitment_info': u'blabla',
            'german_relationship_info': u'blabla',
            'german_risks_info': u'blabla',
            'german_sideeffects_info': u'blabla',
            'german_statistical_info': u'',
            'german_summary': u'blabla',
            'insurance_address': u'',
            'insurance_contract_number': u'',
            'insurance_name': u'',
            'insurance_phone': u'',
            'insurance_validity': u'',
            'invoice_address': u'',
            'invoice_city': u'',
            'invoice_contact_first_name': u'',
            'invoice_contact_gender': None,
            'invoice_contact_last_name': u'',
            'invoice_contact_title': u'',
            'invoice_email': u'',
            'invoice_fax': u'',
            'invoice_name': u'',
            'invoice_phone': u'',
            'invoice_uid': None,
            'invoice_uid_verified_level1': None,
            'invoice_uid_verified_level2': None,
            'invoice_zip_code': u'',
            'medtech_ce_symbol': None,
            'medtech_certified_for_exact_indications': None,
            'medtech_certified_for_other_indications': None,
            'medtech_checked_product': u'',
            'medtech_departure_from_regulations': u'',
            'medtech_manual_included': None,
            'medtech_manufacturer': u'',
            'medtech_product_name': u'',
            'medtech_reference_substance': u'',
            'medtech_technical_safety_regulations': u'',
            'pdf_document_id': None,
            'pharma_checked_substance': u'',
            'pharma_reference_substance': u'',
            'primary_investigator_id': None,
            'project_title': u'Implementation of phones into the ear',
            'project_type_basic_research': True,
            'project_type_biobank': False,
            'project_type_education_context': None,
            'project_type_genetic_study': False,
            'project_type_medical_device': False,
            'project_type_medical_device_performance_evaluation': False,
            'project_type_medical_device_with_ce': False,
            'project_type_medical_device_without_ce': False,
            'project_type_medical_method': True,
            'project_type_misc': u'',
            'project_type_non_reg_drug': False,
            'project_type_psychological_study': False,
            'project_type_questionnaire': False,
            'project_type_reg_drug': False,
            'project_type_reg_drug_not_within_indication': False,
            'project_type_reg_drug_within_indication': False,
            'project_type_register': False,
            'project_type_retrospective': False,
            'protocol_number': u'',
            'specialism': u'Chirurgie',
            'sponsor_address': u'main-street 1',
            'sponsor_agrees_to_publishing': True,
            'sponsor_city': u'Wien',
            'sponsor_contact_first_name': u'John',
            'sponsor_contact_gender': u'm',
            'sponsor_contact_last_name': u'Doe',
            'sponsor_contact_title': u'Dr.',
            'sponsor_email': u'johndoe@example.org',
            'sponsor_fax': u'',
            'sponsor_id': None,
            'sponsor_name': u'John Doe',
            'sponsor_phone': u'+43098765432123456789',
            'sponsor_zip_code': u'4223',
            'study_plan_abort_crit': u'blabla',
            'study_plan_alpha': u'blabla',
            'study_plan_alternative_hypothesis': u'',
            'study_plan_biometric_planning': u'blabla',
            'study_plan_blind': 0,
            'study_plan_controlled': False,
            'study_plan_cross_over': True,
            'study_plan_datamanagement': u'blabla',
            'study_plan_dataprotection_anonalgoritm': u'',
            'study_plan_dataprotection_dvr': u'',
            'study_plan_dataprotection_reason': u'',
            'study_plan_dataquality_checking': u'blabla',
            'study_plan_dropout_ratio': u'blabla',
            'study_plan_equivalence_testing': False,
            'study_plan_factorized': True,
            'study_plan_misc': u'',
            'study_plan_multiple_test_correction_algorithm': u'blabla',
            'study_plan_null_hypothesis': u'',
            'study_plan_number_of_groups': u'',
            'study_plan_observer_blinded': False,
            'study_plan_parallelgroups': False,
            'study_plan_pilot_project': False,
            'study_plan_placebo': False,
            'study_plan_planned_statalgorithm': u'',
            'study_plan_population_intention_to_treat': False,
            'study_plan_population_per_protocol': False,
            'study_plan_power': u'blabla',
            'study_plan_primary_objectives': u'',
            'study_plan_randomized': True,
            'study_plan_sample_frequency': u'',
            'study_plan_secondary_objectives': u'',
            'study_plan_statalgorithm': u'blabla',
            'study_plan_statistics_implementation': u'blabla',
            'study_plan_stratification': u'',
            'subject_childbearing': False,
            'subject_count': 4223,
            'subject_duration': u'2 monate',
            'subject_duration_active': u'jetzt',
            'subject_duration_controls': u'nie',
            'subject_females': True,
            'subject_males': True,
            'subject_maxage': 68,
            'subject_minage': 18,
            'subject_noncompetents': False,
            'subject_planned_total_duration': u'ohne ende',
            'submission_type': None,
            'submitter_contact_first_name': u'John',
            'submitter_contact_gender': u'm',
            'submitter_contact_last_name': u'Doe',
            'submitter_contact_title': u'',
            'submitter_email': u'developer@example.org',
            'submitter_id': 2,
            'submitter_is_authorized_by_sponsor': False,
            'submitter_is_coordinator': False,
            'submitter_is_main_investigator': False,
            'submitter_is_sponsor': False,
            'submitter_jobtitle': u'developer',
            'submitter_organisation': u'open source community',
            'substance_p_c_t_application_type': u'',
            'substance_p_c_t_final_report': None,
            'substance_p_c_t_gcp_rules': None,
            'substance_p_c_t_period': u'',
            'substance_p_c_t_phase': u'',
            'substance_preexisting_clinical_tries': None
        }
    
    patienteninformation_filename = os.path.join(os.path.dirname(__file__), 'tests', 'data', 'menschenrechtserklaerung.pdf')
    with open(patienteninformation_filename, 'rb') as patienteninformation:
        doctype = DocumentType.objects.get(identifier='patientinformation')
        doc = Document.objects.create_from_buffer(patienteninformation.read(), version='1', doctype=doctype, date=datetime.now())
        doc.save()

    test_submission_form['submission'] = submission
    test_submission_form['presenter'] = User.objects.get(email='presenter1@example.org')
    submission_form = SubmissionForm.objects.create(**test_submission_form)

    doc.parent_object = submission_form
    doc.save()
    
