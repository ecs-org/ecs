# -*- coding: utf-8 -*-

from ecs import bootstrap
from ecs.bootstrap.utils import update_instance
from ecs.checklists.models import Checklist, ChecklistBlueprint, ChecklistQuestion
from ecs.workflow.patterns import Generic
from ecs.integration.utils import setup_workflow_graph
from ecs.checklists.bootstrap_settings import checklist_questions
from ecs.utils import Args
from ecs.checklists.workflow import ExternalReview, ExternalReviewReview
from ecs.checklists.workflow import is_external_review_checklist, checklist_review_review_failed


# dummy gettext
_ = lambda s: s

@bootstrap.register()
def checklist_blueprints():
    blueprints = (
        dict(slug='thesis_review', name=_("Thesis Review")),
        dict(slug='expedited_review', name=_("Expedited Review"), multiple=False),
        dict(slug='localec_review', name=_("Local-EC Review"), multiple=False),
        dict(slug='statistic_review', name=_("Statistical Review")),
        dict(slug='legal_review', name=_("Legal and Patient Review")),
        dict(slug='insurance_review', name=_("Insurance Review")),
        dict(slug='gcp_review', name=_("GCP Review")),
        dict(slug='boardmember_review', name=_("Board Member Review"), multiple=True),
        dict(slug='external_review', name=_("External Review"), multiple=True, billing_required=True),
    )

    for blueprint in blueprints:
        b, created = ChecklistBlueprint.objects.get_or_create(slug=blueprint['slug'])
        update_instance(b, blueprint)

    for slug in checklist_questions.keys():
        blueprint = ChecklistBlueprint.objects.get(slug=slug)
        for i, question in enumerate(checklist_questions[slug]):
            number, text = question
            data = {
                'index': i,
                'text': text,
                'description': question.pop('description', u''),
                'is_inverted': question.pop('is_inverted', False),
            }
            cq, created = ChecklistQuestion.objects.get_or_create(blueprint=blueprint, number=number, defaults=data)
            update_instance(cq, data)

@bootstrap.register(depends_on=('ecs.integration.bootstrap.workflow_sync', 'ecs.core.bootstrap.auth_groups', 'ecs.checklists.bootstrap.checklist_blueprints'))
def checklist_workflow():
    EXTERNAL_REVIEW_REVIEW_GROUP = 'External Review Review Group'

    setup_workflow_graph(Checklist,
        auto_start=True, 
        nodes={
            'start': Args(Generic, start=True, name=_("Start")),
            'external_review': Args(ExternalReview, name=_("External Review")),
            'external_review_review': Args(ExternalReviewReview, name=_("External Review Review"), group=EXTERNAL_REVIEW_REVIEW_GROUP),
        },
        edges={
            ('start', 'external_review'): Args(guard=is_external_review_checklist),
            ('external_review', 'external_review_review'): None,
            ('external_review_review', 'external_review'): Args(guard=checklist_review_review_failed),
        }
    )
