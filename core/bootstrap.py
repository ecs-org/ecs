# -*- coding: utf-8 -*-
import os
from datetime import datetime
from copy import deepcopy

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group, Permission
from django.contrib.sites.models import Site

from ecs import bootstrap
from ecs.core.models import ExpeditedReviewCategory, MedicalCategory, EthicsCommission, ChecklistBlueprint, ChecklistQuestion
from ecs.utils import Args
from ecs.workflow.patterns import Generic
from ecs.integration.utils import setup_workflow_graph
from ecs.users.utils import get_or_create_user


# We use this helper function for marking task names as translatable, they are
# getting translated later.
_ = lambda s: s

def _update_instance(instance, d):
    changed = False
    for k,v in d.iteritems():
        if not getattr(instance, k) == v:
            setattr(instance, k, v)
            changed = True
    if changed:
        instance.save()

@bootstrap.register()
def sites():
    sites_list = (
        (1, 'devel', 'localhost'),
        (2, 'shredder', 's.ecsdev.ep3.at'),
        (3, 'testecs', 'test.ecsdev.ep3.at'),
        (4, 'chipper', 'doc.ecsdev.ep3.at'),
    )

    # FIXME: On virtual image creation this somehow must be editable for bootstrapping with the right hostname of the target machine
    for pk, name, domain in sites_list:
        site, created = Site.objects.get_or_create(pk=pk)
        site.name = name
        site.domain = domain
        site.save()


@bootstrap.register(depends_on=('ecs.core.bootstrap.sites',))
def templates():
    from dbtemplates.models import Template
    basedir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    for dirpath, dirnames, filenames in os.walk(basedir):
        if 'wkhtml2pdf' not in dirpath:
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
                tpl.sites = Site.objects.all()
                tpl.save()


@bootstrap.register(depends_on=('ecs.integration.bootstrap.workflow_sync', 'ecs.core.bootstrap.checklist_blueprints'))
def submission_workflow():
    from ecs.core.models import Submission
    from ecs.core.workflow import (InitialReview, Resubmission, CategorizationReview, PaperSubmissionReview, AdditionalReviewSplit,
        AdditionalChecklistReview, ChecklistReview, ExternalChecklistReview, ThesisRecommendationReview, ThesisCategorizationReview,
        ExpeditedRecommendation, ExpeditedRecommendationReview, LocalEcRecommendationReview, BoardMemberReview)
    from ecs.core.workflow import (is_retrospective_thesis, is_acknowledged, is_expedited, has_thesis_recommendation,
        needs_external_review, needs_insurance_review, needs_gcp_review, has_expedited_recommendation,
        is_expedited_or_retrospective_thesis, is_localec, is_acknowledged_and_localec, is_acknowledged_and_not_localec)
    
    thesis_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='thesis_review')
    expedited_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='expedited_review')
    localec_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='localec_review')
    statistical_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='statistic_review')
    insurance_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='insurance_review')
    legal_and_patient_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='legal_review')
    boardmember_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='boardmember_review')
    external_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='external_review')
    additional_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='additional_review')
    gcp_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='gcp_review')
    
    THESIS_REVIEW_GROUP = 'EC-Thesis Review Group'
    THESIS_EXECUTIVE_GROUP = 'EC-Thesis Executive Group'
    EXPEDITED_REVIEW_GROUP = 'Expedited Review Group'
    LOCALEC_REVIEW_GROUP = 'Local-EC Review Group'
    EXECUTIVE_GROUP = 'EC-Executive Board Group'
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
            'categorization_review': Args(CategorizationReview, group=EXECUTIVE_GROUP, name=_("Categorization Review")),
            'additional_review_split': Args(AdditionalReviewSplit, name=_("Additional Review Split")),
            'additional_review': Args(AdditionalChecklistReview, data=additional_review_checklist_blueprint, name=_("Additional Checklist Review")),
            'paper_submission_review': Args(PaperSubmissionReview, group=OFFICE_GROUP, name=_("Paper Submission Review")),
            'legal_and_patient_review': Args(ChecklistReview, data=legal_and_patient_review_checklist_blueprint, name=_("Legal and Patient Review"), group=INTERNAL_REVIEW_GROUP),
            'insurance_review': Args(ChecklistReview, data=insurance_review_checklist_blueprint, name=_("Insurance Review"), group=INSURANCE_REVIEW_GROUP),
            'statistical_review': Args(ChecklistReview, data=statistical_review_checklist_blueprint, name=_("Statistical Review"), group=STATISTIC_REVIEW_GROUP),
            'board_member_review': Args(BoardMemberReview, data=boardmember_review_checklist_blueprint, name=_("Board Member Review"), group=BOARD_MEMBER_GROUP),
            'external_review': Args(ExternalChecklistReview, data=external_review_checklist_blueprint, name=_("External Review"), group=EXTERNAL_REVIEW_GROUP),
            'gcp_review': Args(ChecklistReview, data=gcp_review_checklist_blueprint, name=_("GCP Review"), group=GCP_REVIEW_GROUP),

            # retrospective thesis lane
            'initial_thesis_review': Args(InitialReview, name=_("Initial Thesis Review"), group=THESIS_REVIEW_GROUP),
            'thesis_categorization_review': Args(ThesisCategorizationReview, name=_("Thesis Categorization Review"), group=THESIS_EXECUTIVE_GROUP),
            'thesis_paper_submission_review': Args(PaperSubmissionReview, group=THESIS_REVIEW_GROUP, name=_("Paper Submission Review")),
            'thesis_recommendation': Args(ChecklistReview, data=thesis_review_checklist_blueprint, name=_("Thesis Recommendation"), group=THESIS_EXECUTIVE_GROUP),
            'thesis_recommendation_review': Args(ThesisRecommendationReview, data=thesis_review_checklist_blueprint, name=_("Thesis Recommendation Review"), group=EXECUTIVE_GROUP),

            # expedited_lane
            'expedited_recommendation': Args(ExpeditedRecommendation, data=expedited_review_checklist_blueprint, name=_("Expedited Recommendation"), group=EXPEDITED_REVIEW_GROUP),
            'expedited_recommendation_review': Args(ExpeditedRecommendationReview, data=expedited_review_checklist_blueprint, name=_("Expedited Recommendation Review"), group=EXECUTIVE_GROUP),

            # local ec lane
            'localec_recommendation': Args(ChecklistReview, data=localec_review_checklist_blueprint, name=_("Local EC Recommendation"), group=LOCALEC_REVIEW_GROUP),
            'localec_recommendation_review': Args(LocalEcRecommendationReview, data=localec_review_checklist_blueprint, name=_("Local EC Recommendation Review"), group=INTERNAL_REVIEW_GROUP),
        },
        edges={
            ('start', 'initial_review'): Args(guard=is_retrospective_thesis, negated=True), 
            ('initial_review', 'resubmission'): Args(guard=is_acknowledged, negated=True),
            ('initial_review', 'categorization_review'): Args(guard=is_acknowledged_and_not_localec),
            ('initial_review', 'paper_submission_review'): Args(guard=is_acknowledged_and_not_localec),
            ('resubmission', 'start'): None,

            # retrospective thesis lane
            ('start', 'initial_thesis_review'): Args(guard=is_retrospective_thesis),
            ('initial_thesis_review', 'resubmission'): Args(guard=is_acknowledged, negated=True),
            ('initial_thesis_review', 'thesis_categorization_review'): Args(guard=is_acknowledged),
            ('thesis_categorization_review', 'thesis_recommendation'): Args(guard=is_retrospective_thesis),
            ('thesis_categorization_review', 'thesis_paper_submission_review'): Args(guard=is_retrospective_thesis),
            ('thesis_categorization_review', 'categorization_review'): Args(guard=is_retrospective_thesis, negated=True),
            ('thesis_recommendation', 'thesis_recommendation_review'): Args(guard=has_thesis_recommendation),
            ('thesis_recommendation', 'categorization_review'): Args(guard=has_thesis_recommendation, negated=True),
            ('thesis_recommendation_review', 'categorization_review'): Args(guard=has_thesis_recommendation, negated=True),
            ('categorization_review', 'thesis_categorization_review'): Args(guard=is_retrospective_thesis),

            # expedited lane
            ('categorization_review', 'expedited_recommendation'): Args(guard=is_expedited),
            ('expedited_recommendation', 'expedited_recommendation_review'): Args(guard=has_expedited_recommendation),
            ('expedited_recommendation', 'categorization_review'): Args(guard=has_expedited_recommendation, negated=True),
            ('expedited_recommendation_review', 'categorization_review'): Args(guard=has_expedited_recommendation, negated=True),

            # local ec lane
            ('initial_review', 'localec_recommendation'): Args(guard=is_acknowledged_and_localec),
            ('localec_recommendation', 'localec_recommendation_review'): None,

            ('categorization_review', 'generic_review'): Args(guard=is_expedited_or_retrospective_thesis, negated=True),
            ('categorization_review', 'external_review'): Args(guard=needs_external_review),
            ('categorization_review', 'additional_review_split'): None,
            
            ('additional_review_split', 'additional_review'): None,

            ('generic_review', 'insurance_review'): Args(guard=needs_insurance_review),
            ('generic_review', 'statistical_review'): None,
            ('generic_review', 'legal_and_patient_review'): None,
            ('generic_review', 'gcp_review'): Args(guard=needs_gcp_review),
        }
    )
    

@bootstrap.register(depends_on=('ecs.integration.bootstrap.workflow_sync', 'ecs.core.bootstrap.auth_groups'))
def vote_workflow():
    from ecs.core.models import Vote
    from ecs.core.workflow import VoteFinalization, VoteReview, VoteSigning, VotePublication, VoteB2Review
    from ecs.core.workflow import is_executive_vote_review_required, is_final, is_b2, is_b2upgrade
    
    EXECUTIVE_GROUP = 'EC-Executive Board Group'
    OFFICE_GROUP = 'EC-Office'
    INTERNAL_REVIEW_GROUP = 'EC-Internal Review Group'
    SIGNING_GROUP = 'EC-Signing Group'
    B2_REVIEW_GROUP = 'EC-B2 Review Group'

    setup_workflow_graph(Vote, 
        auto_start=True, 
        nodes={
            'start': Args(Generic, start=True, name=_("Start")),
            'review': Args(Generic, name=_("Review Split")),
            'b2_review': Args(VoteB2Review, name=_("B2 Review"), group=B2_REVIEW_GROUP),
            'executive_vote_finalization': Args(VoteReview, name=_("Executive Vote Finalization"), group=EXECUTIVE_GROUP),
            'executive_vote_review': Args(VoteReview, name=_("Executive Vote Review"), group=EXECUTIVE_GROUP),
            'internal_vote_review': Args(VoteReview, name=_("Internal Vote Review"), group=INTERNAL_REVIEW_GROUP),
            'office_vote_finalization': Args(VoteReview, name=_("Office Vote Finalization"), group=OFFICE_GROUP),
            'office_vote_review': Args(VoteReview, name=_("Office Vote Review"), group=OFFICE_GROUP),
            'final_office_vote_review': Args(VoteReview, name=_("Office Vote Review"), group=OFFICE_GROUP),
            'vote_signing': Args(VoteSigning, group=SIGNING_GROUP, name=_("Vote Signing")),
            'vote_publication': Args(VotePublication, group=OFFICE_GROUP, name=_("Vote Publication")),
        }, 
        edges={
            ('start', 'review'): Args(guard=is_b2upgrade, negated=True),
            ('start', 'office_vote_finalization'): Args(guard=is_b2upgrade),
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
            ('vote_signing', 'vote_publication'): None,
            ('vote_publication', 'b2_review'): Args(guard=is_b2),
        }
    )


@bootstrap.register()
def auth_groups():
    groups = (
        u'EC-Office',
        u'EC-Internal Review Group',
        u'EC-Executive Board Group',
        u'EC-Signing Group',
        u'EC-Statistic Group',
        u'EC-Notification Review Group',
        u'EC-Insurance Reviewer',
        u'EC-Thesis Review Group',
        u'EC-Thesis Executive Group',
        u'EC-B2 Review Group',
        u'Expedited Review Group',
        u'Local-EC Review Group',
        u'EC-Board Member',
        u'External Reviewer',
        u'GCP Review Group',
        u'userswitcher_target',
        u'translators',
        u'sentryusers',
        
    )
    for group in groups:
        Group.objects.get_or_create(name=group)
    
    try:
        p = Permission.objects.get_by_natural_key("can_view", "sentry", "groupedmessage")
        g = Group.objects.get(name="sentryusers")
        g.permissions.add(p)
    except Permission.DoesNotExist:
        print ("Warning: Sentry not active, therefore we can not add Permission to sentryusers")
    

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
        if not medcat.name == longname:
            medcat.name = longname
            medcat.save()


@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups',))
def auth_user_developers():
    ''' Developer Account Creation '''
    try:
        from ecs.core.bootstrap_settings import developers
    except ImportError:
        # first, Last, email, password, gender (sic!)
        developers = ((u'John', u'Doe', u'developer@example.org', 'changeme', 'f'),)
        
    for first, last, email, password, gender in developers:
        user, created = get_or_create_user(email, start_workflow=False)
        user.first_name = first
        user.last_name = last
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.groups.add(Group.objects.get(name="translators"))
        user.groups.add(Group.objects.get(name="sentryusers"))
        user.save()
        profile = user.get_profile()
        profile.approved_by_office = True
        profile.help_writer = True
        profile.forward_messages_after_minutes = 360
        profile.gender = gender
        profile.start_workflow = True
        profile.save()


@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups', 
    'ecs.core.bootstrap.expedited_review_categories', 'ecs.core.bootstrap.medical_categories'))
def auth_user_sentryuser():
        user, created = get_or_create_user('sentry@example.org', start_workflow=False)
        user.groups.add(Group.objects.get(name="userswitcher_target"))
        user.is_staff = True
        user.is_superuser = True
        user.save()
        profile = user.get_profile()
        profile.approved_by_office = True
        profile.start_workflow = True
        profile.save()


@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups', 
    'ecs.core.bootstrap.expedited_review_categories', 'ecs.core.bootstrap.medical_categories'))
def auth_user_testusers():
    ''' Test User Creation, target to userswitcher'''
    testusers = (
        ('presenter', None, {}),
        ('sponsor', None, {}),
        ('investigator', None, {}),
        ('office', u'EC-Office', {'internal': True,}),
        ('internal.rev', u'EC-Internal Review Group', {'internal': True,}),
        ('executive', u'EC-Executive Board Group', {'internal': True, 'executive_board_member': True),
        ('thesis.executive', u'EC-Thesis Executive Group', {'internal': True, 'executive_board_member': True),
        ('signing', u'EC-Signing Group', {'internal': True, }),
        ('statistic.rev', u'EC-Statistic Group', {'internal': False}),
        ('notification.rev', u'EC-Notification Review Group', {'internal': True, }),
        ('insurance.rev', u'EC-Insurance Reviewer', {'internal': False, 'insurance_review': True}),
        ('thesis.rev', u'EC-Thesis Review Group', {'internal': False, 'thesis_review': True),
        ('external.reviewer', u'External Reviewer', {'external_review': True, }),
        ('gcp.reviewer', u'GCP Review Group', {'internal': False}),
        ('localec.rev', u'Local-EC Review Group', {'internal': True}),
        ('b2.rev', u'EC-B2 Review Group', {'internal': True}),
    )

    boardtestusers = (
         ('b.member1.klph', ('KlPh',)),
         ('b.member2.klph.onko', ('KlPh','Onko')),
         ('b.member3.onko', ('Onko',)),
         ('b.member4.infektio', ('Infektio',)),
         ('b.member5.kardio', ('Kardio',)),
         ('b.member6.paed', ('Päd',)), 
    )

    expeditedtestusers = (
         ('expedited.klph', ('KlPh',)),
         ('expedited.stats', ('Stats',)),
         ('expedited.labor', ('Labor',)),
         ('expedited.recht', ('Recht',)),
    )
    
    userswitcher_group = Group.objects.get(name="userswitcher_target")
    boardmember_group = Group.objects.get(name='EC-Board Member')
    expedited_review_group = Group.objects.get(name='Expedited Review Group')

    for testuser, testgroup, flags in testusers:
        for number in range(1,4):
            user, created = get_or_create_user('{0}{1}@example.org'.format(testuser, number), start_workflow=False)
            if testgroup:
                user.groups.add(Group.objects.get(name=testgroup))
            user.groups.add(userswitcher_group)

            profile = user.get_profile()
            for flagname, flagvalue in flags.items():
                setattr(profile, flagname, flagvalue)
            profile.approved_by_office = True
            if number == 3:
                # XXX set every third userswitcher user to be included in help_writer group
                profile.help_writer = True

            profile.start_workflow = True
            profile.save()

    
    for testuser, medcategories in boardtestusers:
        user, created = get_or_create_user('{0}@example.org'.format(testuser), start_workflow=False)
        user.groups.add(boardmember_group)
        user.groups.add(userswitcher_group)

        profile = user.get_profile()
        profile.board_member = True
        profile.approved_by_office = True
        profile.start_workflow = True
        profile.save()

        for medcategory in medcategories:
            m= MedicalCategory.objects.get(abbrev=medcategory)
            m.users.add(user)

    for testuser, expcategories in expeditedtestusers:
        user, created = get_or_create_user('{0}@example.org'.format(testuser), start_workflow=False)
        user.groups.add(expedited_review_group)
        user.groups.add(userswitcher_group)

        profile = user.get_profile()
        profile.expedited_review = True
        profile.approved_by_office = True
        profile.start_workflow = True
        profile.save()

        for expcategory in expcategories:
            e = ExpeditedReviewCategory.objects.get(abbrev=expcategory)
            e.users.add(user)

@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups',))
def auth_ec_staff_users():
    try:
        from ecs.core.bootstrap_settings import staff_users
    except ImportError:
        staff_users = ()
    
    for blueprint in blueprints:
        b, created = ChecklistBlueprint.objects.get_or_create(slug=blueprint['slug'])
        _update_instance(b, blueprint)

    try:
        from ecs.core.bootstrap_settings import checklist_questions
    except ImportError:
        question = [(u'1. Everything fine and positive', u'this is important'),]        
        checklist_questions = {}
        for blueprint in blueprints:
            checklist_questions [blueprint['slug']] = deepcopy(question)

    for slug in checklist_questions.keys():
        blueprint = ChecklistBlueprint.objects.get(slug=slug)
        for number, text, description in checklist_questions[slug]:
            cq, created = ChecklistQuestion.objects.get_or_create(blueprint=blueprint, number=number)
            cq.text = text
            cq.description = description
            cq.save()
