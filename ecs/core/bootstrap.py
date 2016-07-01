from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_noop as _

from ecs import bootstrap
from ecs.core.models import Submission, MedicalCategory, EthicsCommission, AdvancedSettings
from ecs.checklists.models import ChecklistBlueprint
from ecs.utils import Args
from ecs.integration.utils import setup_workflow_graph
from ecs.users.utils import get_or_create_user, get_user
from ecs.core.workflow import (InitialReview, Resubmission, Categorization, PaperSubmissionReview, VotePreparation,
    ChecklistReview, RecommendationReview, ExpeditedRecommendationSplit, B2ResubmissionReview, InitialB2ResubmissionReview)
from ecs.core.workflow import (is_retrospective_thesis, is_acknowledged, is_expedited, has_thesis_recommendation, has_localec_recommendation,
    needs_expedited_recategorization, is_acknowledged_and_initial_submission, is_still_b2,
    needs_executive_b2_review, needs_expedited_vote_preparation, needs_localec_recommendation,
    needs_localec_vote_preparation)


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
    boardmember_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='boardmember_review')
    gcp_review_checklist_blueprint = ChecklistBlueprint.objects.get(slug='gcp_review')

    THESIS_EXECUTIVE_GROUP = 'EC-Thesis Executive Group'
    LOCALEC_REVIEW_GROUP = 'Local-EC Reviewer'
    EXECUTIVE_GROUP = 'EC-Executive Board Member'
    OFFICE_GROUP = 'EC-Office'
    BOARD_MEMBER_GROUP = 'EC-Board Member'
    INSURANCE_REVIEW_GROUP = 'EC-Insurance Reviewer'
    STATISTIC_REVIEW_GROUP = 'EC-Statistic Reviewer'
    INTERNAL_REVIEW_GROUP = 'EC-Internal Reviewer'
    GCP_REVIEW_GROUP = 'GCP Reviewer'
    PAPER_GROUP = 'EC-Paper Submission Reviewer'
    B2_REVIEW_GROUP = 'EC-B2 Reviewer'

    setup_workflow_graph(Submission,
        auto_start=True,
        nodes={
            'resubmission': Args(Resubmission, name=_("Resubmission")),
            'b2_resubmission': Args(Resubmission, name=_("B2 Resubmission")),
            'b2_review': Args(InitialB2ResubmissionReview, name=_("B2 Resubmission Review"), group=B2_REVIEW_GROUP),
            'executive_b2_review': Args(B2ResubmissionReview, name=_("B2 Resubmission Review"), group=EXECUTIVE_GROUP),
            'initial_review': Args(InitialReview, start=True, group=OFFICE_GROUP, name=_("Initial Review")),
            'categorization': Args(Categorization, group=EXECUTIVE_GROUP, name=_("Categorization")),
            'paper_submission_review': Args(PaperSubmissionReview, group=PAPER_GROUP, name=_("Paper Submission Review")),
            'legal_and_patient_review': Args(ChecklistReview, data=legal_and_patient_review_checklist_blueprint, name=_("Legal and Patient Review"), group=INTERNAL_REVIEW_GROUP, is_dynamic=True),
            'insurance_review': Args(ChecklistReview, data=insurance_review_checklist_blueprint, name=_("Insurance Review"), group=INSURANCE_REVIEW_GROUP, is_dynamic=True),
            'statistical_review': Args(ChecklistReview, data=statistical_review_checklist_blueprint, name=_("Statistical Review"), group=STATISTIC_REVIEW_GROUP, is_dynamic=True),
            'board_member_review': Args(ChecklistReview, data=boardmember_review_checklist_blueprint, name=_("Board Member Review"), group=BOARD_MEMBER_GROUP, is_delegatable=False, is_dynamic=True),
            'gcp_review': Args(ChecklistReview, data=gcp_review_checklist_blueprint, name=_("GCP Review"), group=GCP_REVIEW_GROUP, is_dynamic=True),

            # retrospective thesis lane
            'thesis_recommendation': Args(ChecklistReview, data=thesis_review_checklist_blueprint, name=_("Thesis Recommendation"), group=THESIS_EXECUTIVE_GROUP),
            'thesis_recommendation_review': Args(RecommendationReview, data=thesis_review_checklist_blueprint, name=_("Thesis Recommendation Review"), group=EXECUTIVE_GROUP),

            # expedited_lane
            'expedited_recommendation_split': Args(ExpeditedRecommendationSplit, name=_("Expedited Recommendation Split")),
            'expedited_recommendation': Args(ChecklistReview, data=expedited_review_checklist_blueprint, name=_("Expedited Recommendation"), group=BOARD_MEMBER_GROUP),

            # local ec lane
            'localec_recommendation': Args(ChecklistReview, data=localec_review_checklist_blueprint, name=_("Local EC Recommendation"), group=LOCALEC_REVIEW_GROUP),

            # retrospective thesis, expedited and local ec lanes
            'vote_preparation': Args(VotePreparation, name=_("Vote Preparation"), group=OFFICE_GROUP),
        },
        edges={
            ('initial_review', 'resubmission'): Args(guard=is_acknowledged, negated=True),
            ('initial_review', 'categorization'): Args(guard=is_acknowledged_and_initial_submission),
            ('initial_review', 'paper_submission_review'): Args(guard=is_acknowledged_and_initial_submission),
            ('b2_resubmission', 'b2_review'): None,
            ('b2_review', 'executive_b2_review'): Args(guard=needs_executive_b2_review),
            ('b2_review', 'b2_resubmission'): Args(guard=is_still_b2),
            ('executive_b2_review', 'b2_review'): None,

            # retrospective thesis lane
            ('categorization', 'thesis_recommendation'): Args(guard=is_retrospective_thesis),
            ('thesis_recommendation', 'thesis_recommendation_review'): Args(guard=has_thesis_recommendation),
            ('thesis_recommendation', 'categorization'): Args(guard=has_thesis_recommendation, negated=True),
            ('thesis_recommendation_review', 'vote_preparation'): Args(guard=has_thesis_recommendation),
            ('thesis_recommendation_review', 'categorization'): Args(guard=has_thesis_recommendation, negated=True),

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


@bootstrap.register()
def auth_groups():
    groups = (
        'EC-Office',
        'EC-Internal Reviewer',
        'EC-Executive Board Member',
        'EC-Signing',
        'EC-Statistic Reviewer',
        'EC-Notification Reviewer',
        'EC-Insurance Reviewer',
        'EC-Thesis Executive Group',
        'EC-B2 Reviewer',
        'EC-Paper Submission Reviewer',
        'EC-Safety Report Reviewer',
        'Local-EC Reviewer',
        'EC-Board Member',
        'GCP Reviewer',
        'Userswitcher Target',
        'External Reviewer',
        'External Review Reviewer',
        'Meeting Protocol Receiver',
        'Resident Board Member',
        'Omniscient Board Member',
        'Help Writer',
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
    )
    return categories


@bootstrap.register()
def medical_categories():
    for abbrev, name in medcategories():
        MedicalCategory.objects.update_or_create(
            abbrev=abbrev, defaults={'name': name})


@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups',))
def auth_user_developers():
    ''' Developer Account Creation '''
    try:
        from ecs.core.bootstrap_settings import developers
    except ImportError:
        # first, Last, email, gender (sic!)
        developers = (('John', 'Doe', 'developer@example.org', 'f'),)

    help_writer_group = Group.objects.get(name='Help Writer')

    for first, last, email, gender in developers:
        user, created = get_or_create_user(email)
        user.first_name = first
        user.last_name = last
        user.is_staff = False
        user.is_superuser = False
        user.save()

        user.groups.add(help_writer_group)
        user.profile.forward_messages_after_minutes = 30
        user.profile.gender = gender
        user.profile.save()


@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups',
    'ecs.core.bootstrap.medical_categories'))
def auth_user_testusers():
    ''' Test User Creation, target to userswitcher'''
    testusers = (
        ('presenter', None),
        ('sponsor', None),
        ('investigator', None),
        ('office', 'EC-Office'),
        ('internal.rev', 'EC-Internal Reviewer'),
        ('executive', 'EC-Executive Board Member'),
        ('thesis.executive', 'EC-Thesis Executive Group'),
        ('signing', 'EC-Signing'),
        ('signing_fail', 'EC-Signing'),
        ('signing_mock', 'EC-Signing'),
        ('statistic.rev', 'EC-Statistic Reviewer'),
        ('notification.rev', 'EC-Notification Reviewer'),
        ('insurance.rev', 'EC-Insurance Reviewer'),
        ('external.reviewer', None),
        ('gcp.reviewer', 'GCP Reviewer'),
        ('localec.rev', 'Local-EC Reviewer'),
        ('b2.rev', 'EC-B2 Reviewer'),
        ('ext.rev', 'External Reviewer'),
        ('ext.rev.rev', 'External Review Reviewer'),
        ('paper.rev', 'EC-Paper Submission Reviewer'),
        ('safety.rev', 'EC-Safety Report Reviewer'),
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

    userswitcher_group = Group.objects.get(name='Userswitcher Target')
    boardmember_group = Group.objects.get(name='EC-Board Member')
    help_writer_group = Group.objects.get(name='Help Writer')

    for testuser, testgroup in testusers:
        for number in range(1,4):
            user, created = get_or_create_user('{0}{1}@example.org'.format(testuser, number))
            if testgroup:
                user.groups.add(Group.objects.get(name=testgroup))
            user.groups.add(userswitcher_group)
            if number == 3:
                # XXX set every third userswitcher user to be included in help_writer group
                user.groups.add(help_writer_group)

            user.profile.is_testuser = True
            user.profile.update_flags()
            user.profile.save()

    for testuser, medcategories in boardtestusers:
        user, created = get_or_create_user('{0}@example.org'.format(testuser))
        user.groups.add(boardmember_group)
        user.groups.add(userswitcher_group)

        user.profile.is_testuser = True
        user.profile.update_flags()
        user.profile.save()

        for medcategory in medcategories:
            m = MedicalCategory.objects.get(abbrev=medcategory)
            m.users.add(user)

@bootstrap.register()
def ethics_commissions():
    try:
        from ecs.core.bootstrap_settings import commissions
    except ImportError:
        commissions = [{
            'uuid': '12345678909876543212345678909876',
            'city': 'Neverland',
            'fax': None,
            'chairperson': None,
            'name': 'Ethikkommission von Neverland',
            'url': None,
            'email': None,
            'phone': None,
            'address_1': 'Mainstreet 1',
            'contactname': None,
            'address_2': '',
            'zip_code': '4223',
        }]

    for comm in commissions:
        comm = comm.copy()
        EthicsCommission.objects.update_or_create(uuid=comm.pop('uuid'), defaults=comm)

@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_user_testusers',))
def advanced_settings():
    default_contact = get_user('office1@example.org')
    AdvancedSettings.objects.get_or_create(pk=1, defaults={'default_contact': default_contact})
