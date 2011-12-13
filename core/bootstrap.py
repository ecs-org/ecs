# -*- coding: utf-8 -*-
import os
from datetime import datetime
from dbtemplates.models import Template

from django.contrib.auth.models import Group, Permission
from django.contrib.sites.models import Site

from ecs import bootstrap
from ecs.core.models import Submission, ExpeditedReviewCategory, MedicalCategory, EthicsCommission
from ecs.checklists.models import ChecklistBlueprint
from ecs.utils import Args
from ecs.workflow.patterns import Generic
from ecs.integration.utils import setup_workflow_graph
from ecs.users.utils import get_or_create_user
from ecs.bootstrap.utils import update_instance
from ecs.core.workflow import (InitialReview, InitialThesisReview, Resubmission, CategorizationReview, PaperSubmissionReview, VotePreparation,
    ChecklistReview, RecommendationReview, ExpeditedRecommendationSplit, WaitForMeeting, B2ResubmissionReview, InitialB2ResubmissionReview)
from ecs.core.workflow import (is_retrospective_thesis, is_acknowledged, is_expedited, has_thesis_recommendation, has_localec_recommendation,
    needs_insurance_review, needs_gcp_review, needs_legal_and_patient_review, needs_statistical_review, needs_paper_submission_review,
    has_expedited_recommendation, is_expedited_or_retrospective_thesis, is_acknowledged_and_initial_submission, is_b2, is_still_b2,
    needs_insurance_b2_review, needs_executive_b2_review, needs_expedited_vote_preparation, needs_localec_recommendation,
    needs_localec_vote_preparation)


# We use this helper function for marking task names as translatable, they are
# getting translated later.
_ = lambda s: s


# caching lookup function to spare db queries
def _get_group(name, cache={}):
    try:
        g = cache[name]
    except KeyError:
        g = Group.objects.get(name=name)
        cache[name] = g
    return g

def _get_medical_category(abbrev, cache={}):
    try:
        mc = cache[abbrev]
    except KeyError:
        mc = MedicalCategory.objects.get(abbrev=abbrev)
        cache[abbrev] = mc
    return mc

def _get_expedited_category(abbrev, cache={}):
    try:
        ec = cache[abbrev]
    except KeyError:
        ec = ExpeditedReviewCategory.objects.get(abbrev=abbrev)
        cache[abbrev] = ec
    return ec


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
        update_instance(site, {
            'name': name,
            'domain': domain,
        })

@bootstrap.register(depends_on=('ecs.core.bootstrap.sites',))
def templates():
    basedir = os.path.join(os.path.dirname(__file__), '..', 'templates')

    sites = list(Site.objects.all())

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
                tpl, created = Template.objects.get_or_create(name=name)
                if created or tpl.last_changed < datetime.fromtimestamp(os.path.getmtime(path)):
                    # only read the file if we really have to
                    with open(path, 'r') as f:
                        content = f.read()
                    tpl.content = content
                tpl.sites = sites
                tpl.save()


@bootstrap.register(depends_on=('ecs.integration.bootstrap.workflow_sync', 'ecs.core.bootstrap.auth_groups', 'ecs.checklists.bootstrap.checklist_blueprints'))
def submission_workflow():
    thesis_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='thesis_review')
    expedited_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='expedited_review')
    localec_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='localec_review')
    statistical_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='statistic_review')
    insurance_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='insurance_review')
    legal_and_patient_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='legal_review')
    boardmember_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='boardmember_review')
    gcp_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='gcp_review')
    
    THESIS_REVIEW_GROUP = 'EC-Thesis Review Group'
    THESIS_EXECUTIVE_GROUP = 'EC-Thesis Executive Group'
    EXPEDITED_REVIEW_GROUP = 'Expedited Review Group'
    LOCALEC_REVIEW_GROUP = 'Local-EC Review Group'
    EXECUTIVE_GROUP = 'EC-Executive Board Group'
    OFFICE_GROUP = 'EC-Office'
    BOARD_MEMBER_GROUP = 'EC-Board Member'
    INSURANCE_REVIEW_GROUP = 'EC-Insurance Reviewer'
    STATISTIC_REVIEW_GROUP = 'EC-Statistic Group'
    INTERNAL_REVIEW_GROUP = 'EC-Internal Review Group'
    GCP_REVIEW_GROUP = 'GCP Review Group'
    PAPER_GROUP = u'EC-Paper Submission Review Group'
    VOTE_PREPARATION_GROUP = u'EC-Vote Preparation Group'
    B2_REVIEW_GROUP = u'EC-B2 Review Group'
    
    setup_workflow_graph(Submission,
        auto_start=True,
        nodes={
            'start': Args(Generic, start=True, name=_("Start")),
            'generic_review': Args(Generic, name=_("Review Split")),
            'resubmission': Args(Resubmission, name=_("Resubmission")),
            'b2_resubmission': Args(Resubmission, name=_("B2 Resubmission")),
            'b2_review': Args(InitialB2ResubmissionReview, name=_("B2 Resubmission Review"), group=B2_REVIEW_GROUP),
            'insurance_b2_review': Args(B2ResubmissionReview, name=_("B2 Resubmission Review"), group=INSURANCE_REVIEW_GROUP),
            'executive_b2_review': Args(B2ResubmissionReview, name=_("B2 Resubmission Review"), group=EXECUTIVE_GROUP),
            'wait_for_meeting': Args(WaitForMeeting, name=_("Wait For Meeting")),
            'initial_review': Args(InitialReview, group=OFFICE_GROUP, name=_("Initial Review")),
            'initial_review_barrier': Args(Generic, name=_('Initial Review Split')),
            'categorization_review': Args(CategorizationReview, group=EXECUTIVE_GROUP, name=_("Categorization Review")),
            'paper_submission_review': Args(PaperSubmissionReview, group=PAPER_GROUP, name=_("Paper Submission Review")),
            'legal_and_patient_review': Args(ChecklistReview, data=legal_and_patient_review_checklist_blueprint, name=_("Legal and Patient Review"), group=INTERNAL_REVIEW_GROUP),
            'insurance_review': Args(ChecklistReview, data=insurance_review_checklist_blueprint, name=_("Insurance Review"), group=INSURANCE_REVIEW_GROUP),
            'statistical_review': Args(ChecklistReview, data=statistical_review_checklist_blueprint, name=_("Statistical Review"), group=STATISTIC_REVIEW_GROUP),
            'board_member_review': Args(ChecklistReview, data=boardmember_review_checklist_blueprint, name=_("Board Member Review"), group=BOARD_MEMBER_GROUP),
            'gcp_review': Args(ChecklistReview, data=gcp_review_checklist_blueprint, name=_("GCP Review"), group=GCP_REVIEW_GROUP),

            # retrospective thesis lane
            'initial_thesis_review': Args(InitialThesisReview, name=_("Initial Thesis Review"), group=THESIS_REVIEW_GROUP),
            'initial_thesis_review_barrier': Args(Generic, name=_('Initial Thesis Review Split')),
            'thesis_recommendation': Args(ChecklistReview, data=thesis_review_checklist_blueprint, name=_("Thesis Recommendation"), group=THESIS_EXECUTIVE_GROUP),
            'thesis_recommendation_review': Args(RecommendationReview, data=thesis_review_checklist_blueprint, name=_("Thesis Recommendation Review"), group=EXECUTIVE_GROUP),
            'thesis_vote_preparation': Args(VotePreparation, name=_("Thesis Vote Preparation"), group=VOTE_PREPARATION_GROUP),

            # expedited_lane
            'expedited_recommendation_split': Args(ExpeditedRecommendationSplit, name=_("Expedited Recommendation Split")),
            'expedited_recommendation': Args(ChecklistReview, data=expedited_review_checklist_blueprint, name=_("Expedited Recommendation"), group=EXPEDITED_REVIEW_GROUP),
            'expedited_vote_preparation': Args(VotePreparation, name=_("Expedited Vote Preparation"), group=VOTE_PREPARATION_GROUP),

            # local ec lane
            'localec_recommendation': Args(ChecklistReview, data=localec_review_checklist_blueprint, name=_("Local EC Recommendation"), group=LOCALEC_REVIEW_GROUP),
            'localec_vote_preparation': Args(VotePreparation, name=_("Local EC Vote Preparation"), group=VOTE_PREPARATION_GROUP),
        },
        edges={
            ('start', 'initial_review'): Args(guard=is_retrospective_thesis, negated=True),
            ('initial_review', 'resubmission'): Args(guard=is_acknowledged, negated=True),
            ('initial_review', 'initial_review_barrier'): Args(guard=is_acknowledged_and_initial_submission),
            ('initial_review_barrier', 'categorization_review'): None,
            ('initial_review_barrier', 'paper_submission_review'): Args(guard=needs_paper_submission_review),
            ('categorization_review', 'wait_for_meeting'): Args(guard=is_retrospective_thesis, negated=True),
            ('wait_for_meeting', 'b2_resubmission'): Args(guard=is_b2),
            ('b2_resubmission', 'b2_review'): None,
            ('b2_review', 'insurance_b2_review'): Args(guard=needs_insurance_b2_review),
            ('b2_review', 'executive_b2_review'): Args(guard=needs_executive_b2_review),
            ('b2_review', 'b2_resubmission'): Args(guard=is_still_b2),
            ('insurance_b2_review', 'b2_review'): None,
            ('executive_b2_review', 'b2_review'): None,

            # retrospective thesis lane
            ('start', 'initial_thesis_review'): Args(guard=is_retrospective_thesis),
            ('initial_thesis_review', 'resubmission'): Args(guard=is_acknowledged, negated=True),
            ('initial_thesis_review', 'initial_thesis_review_barrier'): Args(guard=is_acknowledged_and_initial_submission),
            ('initial_thesis_review_barrier', 'wait_for_meeting'): Args(guard=is_retrospective_thesis),
            ('initial_thesis_review_barrier', 'thesis_recommendation'): Args(guard=is_retrospective_thesis),
            ('initial_thesis_review_barrier', 'paper_submission_review'): Args(guard=is_retrospective_thesis),
            ('initial_thesis_review_barrier', 'categorization_review'): Args(guard=is_retrospective_thesis, negated=True),
            ('thesis_recommendation', 'thesis_recommendation_review'): Args(guard=has_thesis_recommendation),
            ('thesis_recommendation', 'categorization_review'): Args(guard=has_thesis_recommendation, negated=True),
            ('thesis_recommendation_review', 'thesis_vote_preparation'): Args(guard=has_thesis_recommendation),
            ('thesis_recommendation_review', 'categorization_review'): Args(guard=has_thesis_recommendation, negated=True),
            ('categorization_review', 'thesis_recommendation'): Args(guard=is_retrospective_thesis),

            # expedited lane
            ('categorization_review', 'expedited_recommendation_split'): None,
            ('expedited_recommendation_split', 'expedited_recommendation'): Args(guard=is_expedited),
            ('expedited_recommendation', 'expedited_vote_preparation'): Args(guard=needs_expedited_vote_preparation),
            ('expedited_recommendation', 'categorization_review'): Args(guard=has_expedited_recommendation, negated=True),

            # local ec lane
            ('categorization_review', 'localec_recommendation'): Args(guard=needs_localec_recommendation),
            ('localec_recommendation', 'localec_vote_preparation'): Args(guard=needs_localec_vote_preparation),
            ('localec_recommendation', 'categorization_review'): Args(guard=has_localec_recommendation, negated=True),

            ('categorization_review', 'generic_review'): Args(guard=is_expedited_or_retrospective_thesis, negated=True),
            ('generic_review', 'insurance_review'): Args(guard=needs_insurance_review),
            ('generic_review', 'statistical_review'): Args(guard=needs_statistical_review),
            ('generic_review', 'legal_and_patient_review'): Args(guard=needs_legal_and_patient_review),
            ('generic_review', 'gcp_review'): Args(guard=needs_gcp_review),
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
        u'EC-Paper Submission Review Group',
        u'EC-Safety Report Review Group',
        u'Expedited Review Group',
        u'Local-EC Review Group',
        u'EC-Board Member',
        u'GCP Review Group',
        u'userswitcher_target',
        u'translators',
        u'sentryusers',
        u'External Review Review Group',
        u'EC-Vote Preparation Group',
        u'Vote Receiver Group',
        u'Amendment Receiver Group',
        u'Meeting Protocol Receiver Group',
        u'Resident Board Member Group',
    )
    for group in groups:
        Group.objects.get_or_create(name=group)
    
    try:
        p = Permission.objects.get_by_natural_key("can_view", "sentry", "groupedmessage")
        g = Group.objects.get(name="sentryusers")
        g.permissions.add(p)
    except Permission.DoesNotExist:
        print ("Warning: Sentry not active, therefore we can not add Permission to sentryusers")
    

def medcategories():
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
        (u'Psych', u'Psychiatrie'),
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

        (u'Pfleger', u'Gesundheits und Krankenpflege'),
        (u'Recht', u'Juristen'),
        (u'Apotheke', u'Pharmazie'),
        (u'Patient', u'Patientenvertretung'), 
        (u'BehinOrg', u'Behindertenorganisation'), 
        (u'Seel', u'Seelsorger'),
        (u'techSec', u'technische Sicherheitsbeauftragte'),

        (u'Psychol', u'Psychologie'),
        (u'Virologie', u'Virologie'),
        (u'Tropen', u'Tropen'),
        (u'Ernährung', u'Ernährung'),
        (u'Hygiene', u'Hygiene'),
        (u'MedPhy', u'Medizinische Physik'),
        (u'Unfall', u'Unfallchirurgie'),
    )
    return categories

@bootstrap.register()
def expedited_review_categories():
    for abbrev, name in medcategories():
        erc, created = ExpeditedReviewCategory.objects.get_or_create(abbrev=abbrev, defaults={'name': name})
        update_instance(erc, {'name': name})


@bootstrap.register()
def medical_categories():
    for abbrev, name in medcategories():
        medcat, created = MedicalCategory.objects.get_or_create(abbrev=abbrev, defaults={'name': name})
        update_instance(medcat, {'name': name})


@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups',))
def auth_user_developers():
    ''' Developer Account Creation '''
    try:
        from ecs.core.bootstrap_settings import developers
    except ImportError:
        # first, Last, email, password, gender (sic!)
        developers = ((u'John', u'Doe', u'developer@example.org', 'changeme', 'f'),)

    translators_group = _get_group('translators')
    sentry_group = _get_group('sentryusers')

    for first, last, email, password, gender in developers:
        user, created = get_or_create_user(email, start_workflow=False)
        user.first_name = first
        user.last_name = last
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.groups.add(translators_group)
        user.groups.add(sentry_group)
        user.save()
        profile = user.get_profile()
        update_instance(profile, {
            'is_help_writer': True,
            'forward_messages_after_minutes': 360,
            'gender': gender,
            'start_workflow': True,
        })

@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups', 
    'ecs.core.bootstrap.expedited_review_categories', 'ecs.core.bootstrap.medical_categories'))
def auth_user_sentryuser():
        user, created = get_or_create_user('sentry@example.org', start_workflow=False)
        user.groups.add(_get_group('userswitcher_target'))
        user.is_staff = True
        user.is_superuser = True
        user.save()
        profile = user.get_profile()
        update_instance(profile, {                        
            "start_workflow" : True,
        })


@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups', 
    'ecs.core.bootstrap.expedited_review_categories', 'ecs.core.bootstrap.medical_categories'))
def auth_user_testusers():
    ''' Test User Creation, target to userswitcher'''
    testusers = (
        ('presenter', None, {}),
        ('sponsor', None, {}),
        ('investigator', None, {}),
        ('office', u'EC-Office', {'is_internal': True,}),
        ('internal.rev', u'EC-Internal Review Group', {'is_internal': True,}),
        ('executive', u'EC-Executive Board Group', {'is_internal': True, 'is_executive_board_member': True),
        ('thesis.executive', u'EC-Thesis Executive Group', {'is_internal': False, 'is_executive_board_member': False),
        ('signing', u'EC-Signing Group', {'is_internal': True, }),
        ('signing_fail', u'EC-Signing Group', {'is_internal': True }),
        ('signing_mock', u'EC-Signing Group', {'is_internal': True }),
        ('statistic.rev', u'EC-Statistic Group', {'is_internal': False}),
        ('notification.rev', u'EC-Notification Review Group', {'is_internal': True, }),
        ('insurance.rev', u'EC-Insurance Reviewer', {'is_internal': False, 'is_insurance_reviewer': True}),
        ('thesis.rev', u'EC-Thesis Review Group', {'is_internal': False, 'is_thesis_reviewer': True),
        ('external.reviewer', None, {}),
        ('gcp.reviewer', u'GCP Review Group', {'is_internal': False}),
        ('localec.rev', u'Local-EC Review Group', {'is_internal': True}),
        ('b2.rev', u'EC-B2 Review Group', {'is_internal': True}),
        ('ext.rev.rev', u'External Review Review Group', {'is_internal': True}),
        ('paper.rev', u'EC-Paper Submission Review Group', {'is_internal': True}),
        ('safety.rev', u'EC-Safety Report Review Group', {'is_internal': True}),
        ('vote.prep', u'EC-Vote Preparation Group', {'is_internal': True}),
    )

    boardtestusers = (
         ('b.member1.klph', ('KlPh',)),
         ('b.member2.radio.klph', ('Radio', 'KlPh', )),
         ('b.member3.anästh', ('Anästh',)),
         ('b.member4.chir', ('Chir',)),
         ('b.member5.nephro', ('Nephro',)),
         ('b.member6.psychol', ('Psychol',)), 
         ('b.member7.gastro', ('Gastro',)),
         ('b.member8.neuro', ('Neuro',)),
         ('b.member9.angio', ('Angio',)),
    )      
    expeditedtestusers = (
         ('expedited.klph', ('KlPh',)),
         ('expedited.stats', ('Stats',)),
         ('expedited.labor', ('Labor',)),
         ('expedited.recht', ('Recht',)),
    )
    
    userswitcher_group = _get_group('userswitcher_target')
    boardmember_group = _get_group('EC-Board Member')
    expedited_review_group = _get_group('Expedited Review Group')

    for testuser, testgroup, flags in testusers:
        for number in range(1,4):
            user, created = get_or_create_user('{0}{1}@example.org'.format(testuser, number), start_workflow=False)
            if testgroup:
                user.groups.add(_get_group(testgroup))
            user.groups.add(userswitcher_group)

            profile = user.get_profile()
            flags = flags.copy()
            flags.update({
                'start_workflow': True,
            })
            if number == 3:
                # XXX set every third userswitcher user to be included in help_writer group
                flags['is_help_writer'] = True
            update_instance(profile, flags)

    for testuser, medcategories in boardtestusers:
        user, created = get_or_create_user('{0}@example.org'.format(testuser), start_workflow=False)
        user.groups.add(boardmember_group)
        user.groups.add(userswitcher_group)

        profile = user.get_profile()
        update_instance(profile, {
            'is_board_member': True,
            'start_workflow': True,
        })
    
        for medcategory in medcategories:
            m = _get_medical_category(medcategory)
            m.users.add(user)

    for testuser, expcategories in expeditedtestusers:
        user, created = get_or_create_user('{0}@example.org'.format(testuser), start_workflow=False)
        user.groups.add(expedited_review_group)
        user.groups.add(userswitcher_group)

        profile = user.get_profile()
        update_instance(profile, {
            'is_expedited_reviewer': True,
            'start_workflow': True,
        })
        
        for expcategory in expcategories:
            e = _get_expedited_category(expcategory)
            e.users.add(user)

@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups',))
def auth_ec_staff_users():
    try:
        from ecs.core.bootstrap_settings import staff_users
    except ImportError:
        staff_users = ((u'Staff', u'User', u'staff@example.org', 'changeme', ('EC-Office',), {},'f'),)

    for first, last, email, password, groups, flags, gender in staff_users:
        user, created = get_or_create_user(email, start_workflow=False)
        user.first_name = first
        user.last_name = last
        user.set_password(password)
        user.is_staff = True
        user.save()
        for group in groups:
            user.groups.add(_get_group(group))

        profile = user.get_profile()
        flags = flags.copy()
        flags.update({
            'is_internal': True,
            'start_workflow': True,
            'forward_messages_after_minutes': 360,
            'gender': gender,
        })
        update_instance(profile, flags)

@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups',
    'ecs.core.bootstrap.expedited_review_categories', 'ecs.core.bootstrap.medical_categories'))
def auth_external_review_users():
    try:
        from ecs.core.bootstrap_settings import external_review_users
    except ImportError:
        other_users = ((u'External', u'Reviewer', u'otherexternal@example.org', 'changeme','f'),)

    for first, last, email, password, gender in external_review_users:
        user, created = get_or_create_user(email, start_workflow=False)
        if created:
            user.first_name = first
            user.last_name = last
            user.set_password(password)
            user.save()

        profile = user.get_profile()
        update_instance(profile, {
            'start_workflow': True,
            'gender': gender,
        })

@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups',
    'ecs.core.bootstrap.expedited_review_categories', 'ecs.core.bootstrap.medical_categories'))
def auth_ec_other_users():
    try:
        from ecs.core.bootstrap_settings import other_users
    except ImportError:
        other_users = ((u'Other', u'User', u'other@example.org', 'changeme', ('EC-Statistic Group',),'f'),)

    for first, last, email, password, groups, gender in other_users:
        user, created = get_or_create_user(email, start_workflow=False)
        if created:
            user.first_name = first
            user.last_name = last
            user.set_password(password)
            user.save()
        for group in groups:
            user.groups.add(_get_group(group))

        profile = user.get_profile()
        update_instance(profile, {
            'start_workflow': True,
            'gender': gender,
            #'forward_messages_after_minutes': 360,
        })

@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups',
    'ecs.core.bootstrap.expedited_review_categories', 'ecs.core.bootstrap.medical_categories'))
def auth_ec_boardmember_users():
    try:
        from ecs.core.bootstrap_settings import board_members
    except ImportError:
        board_members = ((u'Board', u'Member', u'boardmember@example.org', 'changeme', ('Pharma',),'f'),)

    board_member_group = _get_group('EC-Board Member')
    for first, last, email, password, medcategories, gender in board_members:
        user, created = get_or_create_user(email, start_workflow=False)
        if created:
            user.first_name = first
            user.last_name = last
            user.set_password(password)
            user.save()
        user.groups.add(board_member_group)

        profile = user.get_profile()

        profile_data = {
            'is_board_member': True,
            'start_workflow': True,
            'gender': gender,
            #'forward_messages_after_minutes': 360,
        }

        for medcategory in medcategories:
            m = _get_medical_category(medcategory)
            m.users.add(user)
            try:
                e = _get_expedited_category(medcategory)
                e.users.add(user)
                profile_data['is_expedited_reviewer'] = True
            except ExpeditedReviewCategory.DoesNotExist:
                pass

        update_instance(profile, profile_data)

@bootstrap.register()
def ethics_commissions():
    try:
        from ecs.core.bootstrap_settings import commissions
    except ImportError:
        commissions = [{
            'uuid': u'12345678909876543212345678909876',
            'city': u'Neverland',
            'fax': None,
            'chairperson': None,
            'name': u'Ethikkommission von Neverland',
            'url': None,
            'email': None,
            'phone': None,
            'address_1': u'Mainstreet 1',
            'contactname': None,
            'address_2': u'',
            'zip_code': u'4223',
        }]

    for comm in commissions:
        comm = comm.copy()
        ec, created = EthicsCommission.objects.get_or_create(uuid=comm.pop('uuid'), defaults=comm)
        update_instance(ec, comm)
