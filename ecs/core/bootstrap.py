from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_noop as _

from ecs import bootstrap
from ecs.core.models import Submission, MedicalCategory, EthicsCommission, AdvancedSettings
from ecs.checklists.models import ChecklistBlueprint
from ecs.utils import Args
from ecs.workflow.patterns import Generic
from ecs.integration.utils import setup_workflow_graph
from ecs.users.utils import get_or_create_user, get_user
from ecs.core.workflow import (
    InitialReview, Resubmission, Categorization, CategorizationReview,
    PaperSubmissionReview, VotePreparation, ChecklistReview,
    ExpeditedRecommendationSplit, B2ResubmissionReview,
    InitialB2ResubmissionReview,
)
from ecs.core.workflow import (
    is_retrospective_thesis, is_acknowledged, is_expedited,
    has_thesis_recommendation, has_localec_recommendation,
    needs_expedited_recategorization, is_acknowledged_and_initial_submission,
    is_still_b2, needs_executive_b2_review, needs_thesis_vote_preparation,
    needs_expedited_vote_preparation, needs_localec_recommendation,
    needs_localec_vote_preparation, needs_categorization_review,
)


@bootstrap.register()
def sites():
    Site.objects.get_or_create(pk=1,
        defaults={'name': 'dummy', 'domain': 'localhost'})


@bootstrap.register(depends_on=('ecs.integration.bootstrap.workflow_sync', 'ecs.core.bootstrap.auth_groups', 'ecs.checklists.bootstrap.checklist_blueprints'))
def submission_workflow():
    thesis_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='thesis_review')
    expedited_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='expedited_review')
    localec_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='localec_review')
    statistical_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='statistic_review')
    insurance_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='insurance_review')
    legal_and_patient_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='legal_review')
    specialist_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='specialist_review')
    gcp_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='gcp_review')

    EXECUTIVE_GROUP = 'EC-Executive'
    OFFICE_GROUP = 'EC-Office'
    BOARD_MEMBER_GROUP = 'Board Member'
    INSURANCE_REVIEW_GROUP = 'Insurance Reviewer'
    STATISTIC_REVIEW_GROUP = 'Statistic Reviewer'
    GCP_REVIEW_GROUP = 'GCP Reviewer'
    SPECIALIST_GROUP = 'Specialist'

    setup_workflow_graph(Submission,
        auto_start=True,
        nodes={
            'start': Args(Generic, start=True, name="Start"),
            'resubmission': Args(Resubmission, name=_("Resubmission")),
            'b2_resubmission': Args(Resubmission, name=_("B2 Resubmission")),
            'b2_review': Args(InitialB2ResubmissionReview, name=_("Office B2 Resubmission Review"), group=OFFICE_GROUP),
            'executive_b2_review': Args(B2ResubmissionReview, name=_("Executive B2 Resubmission Review"), group=EXECUTIVE_GROUP),
            'initial_review': Args(InitialReview, group=OFFICE_GROUP, name=_("Initial Review")),
            'initial_review_barrier': Args(Generic, name="Initial Review Barrier"),
            'categorization': Args(Categorization, group=EXECUTIVE_GROUP, name=_("Categorization")),
            'categorization_review': Args(CategorizationReview, group=OFFICE_GROUP, name=_("Categorization Review")),
            'paper_submission_review': Args(PaperSubmissionReview, group=OFFICE_GROUP, name=_("Paper Submission Review")),
            'legal_and_patient_review': Args(ChecklistReview, data=legal_and_patient_review_checklist_blueprint, name=_("Legal and Patient Review"), group=OFFICE_GROUP, is_dynamic=True),
            'insurance_review': Args(ChecklistReview, data=insurance_review_checklist_blueprint, name=_("Insurance Review"), group=INSURANCE_REVIEW_GROUP, is_dynamic=True),
            'statistical_review': Args(ChecklistReview, data=statistical_review_checklist_blueprint, name=_("Statistical Review"), group=STATISTIC_REVIEW_GROUP, is_dynamic=True),
            'specialist_review': Args(ChecklistReview, data=specialist_review_checklist_blueprint, name=_("Specialist Review"), group=SPECIALIST_GROUP, is_delegatable=False, is_dynamic=True),
            'gcp_review': Args(ChecklistReview, data=gcp_review_checklist_blueprint, name=_("GCP Review"), group=GCP_REVIEW_GROUP, is_dynamic=True),

            # retrospective thesis lane
            'initial_thesis_review': Args(InitialReview, name=_("Initial Thesis Review"), group=OFFICE_GROUP),
            'thesis_recommendation': Args(ChecklistReview, data=thesis_review_checklist_blueprint, name=_("Thesis Recommendation"), group=OFFICE_GROUP),

            # expedited_lane
            'expedited_recommendation_split': Args(ExpeditedRecommendationSplit, name=_("Expedited Recommendation Split")),
            'expedited_recommendation': Args(ChecklistReview, data=expedited_review_checklist_blueprint, name=_("Expedited Recommendation"), group=BOARD_MEMBER_GROUP),

            # local ec lane
            'localec_recommendation': Args(ChecklistReview, data=localec_review_checklist_blueprint, name=_("Local EC Recommendation"), group=EXECUTIVE_GROUP),

            # retrospective thesis, expedited and local ec lanes
            'vote_preparation': Args(VotePreparation, name=_("Vote Preparation"), group=OFFICE_GROUP),
        },
        edges={
            ('start', 'initial_review'): Args(guard=is_retrospective_thesis, negated=True),
            ('start', 'initial_thesis_review'): Args(guard=is_retrospective_thesis),

            ('initial_review', 'initial_review_barrier'): None,
            ('initial_thesis_review', 'initial_review_barrier'): None,
            ('initial_review_barrier', 'resubmission'): Args(guard=is_acknowledged, negated=True),
            ('initial_review_barrier', 'categorization'): Args(guard=is_acknowledged_and_initial_submission),
            ('categorization', 'categorization_review'): Args(guard=needs_categorization_review),
            ('initial_review_barrier', 'paper_submission_review'): Args(guard=is_acknowledged_and_initial_submission),
            ('b2_resubmission', 'b2_review'): None,
            ('b2_review', 'executive_b2_review'): Args(guard=needs_executive_b2_review),
            ('b2_review', 'b2_resubmission'): Args(guard=is_still_b2),
            ('executive_b2_review', 'b2_review'): None,

            # retrospective thesis lane
            ('categorization', 'thesis_recommendation'): Args(guard=is_retrospective_thesis),
            ('thesis_recommendation', 'categorization'): Args(guard=has_thesis_recommendation, negated=True),
            ('thesis_recommendation', 'vote_preparation'): Args(guard=needs_thesis_vote_preparation),

            # expedited lane
            ('categorization', 'expedited_recommendation_split'): None,
            ('expedited_recommendation_split', 'expedited_recommendation'): Args(guard=is_expedited),
            ('expedited_recommendation', 'vote_preparation'): Args(guard=needs_expedited_vote_preparation),
            ('expedited_recommendation', 'categorization'): Args(guard=needs_expedited_recategorization),

            # local ec lane
            ('categorization', 'localec_recommendation'): Args(guard=needs_localec_recommendation),
            ('localec_recommendation', 'vote_preparation'): Args(guard=needs_localec_vote_preparation),
            ('localec_recommendation', 'categorization'): Args(guard=has_localec_recommendation, negated=True),
        }
    )

    # translations for legacy task types
    _('Executive Vote Finalization')
    _('Insurance Amendment Review')
    _('Insurance B2 Resubmission Review')
    _('Office Vote Review (legacy)')
    _('Thesis Recommendation Review')


@bootstrap.register()
def auth_groups():
    groups = (
        'Board Member',
        'EC-Executive',
        'EC-Office',
        'EC-Signing',
        'External Reviewer',
        'GCP Reviewer',
        'Insurance Reviewer',
        'Meeting Protocol Receiver',
        'Omniscient Board Member',
        'Resident Board Member',
        'Specialist',
        'Statistic Reviewer',
        'Userswitcher Target',
    )
    for group in groups:
        Group.objects.get_or_create(name=group)


def medcategories():
    categories = (
        ('Stats', 'Statistik'),
        ('Pharma', 'Pharmakologie'),
        ('KlPh', 'Klinische Pharmakologie'),
        ('Onko', 'Onkologie'),
        ('Häm', 'Hämatologie'),
        ('Infektio', 'Infektiologie'),
        ('Kardio', 'Kardiologie'),
        ('Angio', 'Angiologie'),
        ('Pulmo', 'Pulmologie'),
        ('Endo', 'Endokrinologie'),
        ('Nephro', 'Nephrologie'),
        ('Gastro', 'Gastroenterologie'),
        ('Rheuma', 'Rheumatologie'),
        ('Intensiv', 'Intensivmedizin'),
        ('Chir', 'Chirurgie'),
        ('plChir', 'Plastische Chirurgie'),
        ('HTChir', 'Herz-Thorax Chirurgie'),
        ('KiChir', 'Kinder Chirurgie'),
        ('NeuroChir', 'Neurochirurgie'),
        ('Gyn', 'Gynäkologie'),
        ('HNO', 'Hals-Nasen-Ohrenkrankheiten'),
        ('Anästh', 'Anästhesie'),
        ('Neuro', 'Neurologie'),
        ('Psych', 'Psychiatrie'),
        ('Päd', 'Pädiatrie'),
        ('Derma', 'Dermatologie'),
        ('Radio', 'Radiologie'),
        ('Transfus', 'Transfusionsmedizin'),
        ('Ortho', 'Orthopädie'),
        ('Uro', 'Urologie'),
        ('Notfall', 'Notfallmedizin'),
        ('PhysMed', 'Physikalische Medizin'),
        ('PsychAna', 'Psychoanalyse'),
        ('Auge', 'Ophthalmologie'),
        ('Nuklear', 'Nuklearmedizin'),
        ('Labor', 'Labormedizin'),
        ('Physiol', 'Physiologie'),
        ('Anatomie', 'Anatomie'),
        ('Zahn', 'Zahnheilkunde'),
        ('ImmunPatho', 'Immunpathologie'),
        ('Patho', 'Pathologie'),

        ('Pfleger', 'Gesundheits und Krankenpflege'),
        ('Recht', 'Juristen'),
        ('Apotheke', 'Pharmazie'),
        ('Patient', 'Patientenvertretung'),
        ('BehinOrg', 'Behindertenorganisation'),
        ('Seel', 'Seelsorger'),
        ('techSec', 'technische Sicherheitsbeauftragte'),

        ('Psychol', 'Psychologie'),
        ('Virologie', 'Virologie'),
        ('Tropen', 'Tropen'),
        ('Ernährung', 'Ernährung'),
        ('Hygiene', 'Hygiene'),
        ('MedPhy', 'Medizinische Physik'),
        ('Unfall', 'Unfallchirurgie'),
        ('PubHealth', 'Public Health'),
        ('fMRTPsych', 'fMRT Psychologie'),

        ('Wartesaal', 'Wartesaal'),
        ('FH-Wien', 'FH-Wien'),
        ('St.Anna', 'St. Anna Kinderspital'),
        ('Med1Phy', 'Medizinische Physik 1'),
        ('Datenbank', 'Datenbank'),
        ('StrahlenTh', 'Strahlentherapie'),
        ('KJP', 'Kinder- und Jugendpsychiatrie'),
        ('Neonat', 'Neonatologie'),
        ('Ursprung', 'Ursprungsstudie'),
    )
    return categories


@bootstrap.register()
def medical_categories():
    for abbrev, name in medcategories():
        MedicalCategory.objects.update_or_create(
            abbrev=abbrev, defaults={'name': name})


# @bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups',))
def auth_user_developers():
    ''' Developer Account Creation '''
    developers = (
    )
    for first, last, email, gender in developers:
        user, created = get_or_create_user(email)
        user.first_name = first
        user.last_name = last
        user.is_staff = False
        user.is_superuser = False
        user.save()

        user.profile.forward_messages_after_minutes = 30
        user.profile.gender = gender
        user.profile.save()


@bootstrap.register(depends_on=(
    'ecs.core.bootstrap.auth_groups',
    'ecs.core.bootstrap.medical_categories',
    'ecs.checklists.bootstrap.checklist_workflow',
    'ecs.core.bootstrap.submission_workflow',
    'ecs.notifications.bootstrap.notification_workflow',
    'ecs.votes.bootstrap.vote_workflow',
))
def auth_user_testusers():
    ''' Test User Creation, target to userswitcher'''
    testusers = (
        ('presenter', None),
        ('sponsor', None),
        ('investigator', None),
        ('office', 'EC-Office'),
        ('executive', 'EC-Executive'),
        ('signing', 'EC-Signing'),
        ('signing_fail', 'EC-Signing'),
        ('signing_mock', 'EC-Signing'),
        ('statistic.rev', 'Statistic Reviewer'),
        ('insurance.rev', 'Insurance Reviewer'),
        ('external.reviewer', None),
        ('gcp.reviewer', 'GCP Reviewer'),
        ('ext.rev', 'External Reviewer'),
    )

    boardtestusers = (
         ('b.member1.klph', ('KlPh',)),
         ('b.member2.radio.klph', ('Radio', 'KlPh', )),
         ('b.member3.anaesth', ('Anästh',)),
         ('b.member4.chir', ('Chir',)),
         ('b.member5.nephro', ('Nephro',)),
         ('b.member6.psychol', ('Psychol',)),
         ('b.member7.gastro', ('Gastro',)),
         ('b.member8.neuro', ('Neuro',)),
         ('b.member9.angio', ('Angio',)),
    )

    userswitcher_group = Group.objects.get(name='Userswitcher Target')
    boardmember_group = Group.objects.get(name='Board Member')
    specialist_group = Group.objects.get(name='Specialist')

    for testuser, group in testusers:
        for number in range(1,4):
            user, created = get_or_create_user('{0}{1}@example.org'.format(testuser, number))
            if group:
                group = Group.objects.get(name=group)
                user.groups.add(group)
                if group.name in ('EC-Executive', 'EC-Office', 'EC-Signing'):
                    uids = set(user.profile.task_uids)
                    uids.update(group.task_types.values_list(
                        'workflow_node__uid', flat=True).distinct())
                    user.profile.task_uids = list(uids)

            user.groups.add(userswitcher_group)

            user.profile.is_testuser = True
            user.profile.update_flags()
            user.profile.save()

    for testuser, medcategories in boardtestusers:
        user, created = get_or_create_user('{0}@example.org'.format(testuser))
        user.groups.add(boardmember_group)
        user.groups.add(specialist_group)
        user.groups.add(userswitcher_group)

        user.profile.is_testuser = True
        user.profile.update_flags()
        user.profile.save()

        for medcategory in medcategories:
            m = MedicalCategory.objects.get(abbrev=medcategory)
            m.users.add(user)

@bootstrap.register()
def ethics_commissions():
    test_commission = {
        'uuid': 'ecececececececececececececececec',
        'name': 'Test Ethikkommission',
    }
    from ecs.core.bootstrap_settings import commissions

    if settings.ETHICS_COMMISSION_UUID == test_commission['uuid']:
        commissions += [test_commission]

    for comm in commissions:
        comm = comm.copy()
        EthicsCommission.objects.update_or_create(uuid=comm.pop('uuid'), defaults=comm)

@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_user_testusers',))
def advanced_settings():
    default_contact = get_user('office1@example.org')
    AdvancedSettings.objects.get_or_create(pk=1, defaults={'default_contact': default_contact})
