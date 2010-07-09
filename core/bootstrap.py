# -*- coding: utf-8 -*-
import os, datetime
from ecs import bootstrap
from ecs.core.models import DocumentType, NotificationType, ExpeditedReviewCategory, Submission, MedicalCategory
from ecs.workflow.models import Graph, Node, Edge
from ecs.workflow import patterns
from django.core.management.base import CommandError
from django.core.management import call_command
from django.contrib.auth.models import Group, User


@bootstrap.register()
def document_types():
    names = (
        u"Patienteninformation",
        u"Covering Letter",
        u"Versicherungsbest\u00e4tigung",
        u"Investigator's Brochure",
        u"CRF",
        u"PI's Curriculum Vit\u00e6",
        u"U. gem\u00e4\u00df EU-Direktive 2001-20-EG",
        u"Conflict of Interest",
        u"Protokoll",
    )
    
    for name in names:
        DocumentType.objects.get_or_create(name=name)


@bootstrap.register()
def notification_types():
    types = (
        (u"SAE Bericht", "ecs.core.forms.NotificationForm"),
        (u"Abschlussbericht", "ecs.core.forms.CompletionReportNotificationForm"),
        (u"Zwischenbericht", "ecs.core.forms.ProgressReportNotificationForm"),
        (u"Protokolländerung", "ecs.core.forms.NotificationForm"),
    )
    
    for name, form in types:
        NotificationType.objects.get_or_create(name=name, form=form)
        

@bootstrap.register()
def expedited_review_categories():
    for i in range(5):
        ExpeditedReviewCategory.objects.get_or_create(abbrev="ExRC%s" % i, name="Expedited Review Category #%s" % i)

@bootstrap.register()
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
                print name
                content = open(path, 'r').read()
                tpl, created = Template.objects.get_or_create(name=name, defaults={'content': content})
                if not created and tpl.last_changed < datetime.datetime.fromtimestamp(os.path.getmtime(path)):
                    tpl.content = content
                    tpl.save()

@bootstrap.register()
def submission_workflow():
    call_command('workflow_sync', quiet=True)

    from ecs.core import workflow as cwf
    
    nodes = {
        'initial_review': dict(nodetype=cwf.inspect_form_and_content_completeness, start=True, name="Formal R."),
        'not_retrospective_thesis': dict(nodetype=patterns.generic, name="Review Split"),
        'reject': dict(nodetype=cwf.reject, end=True),
        'accept': dict(nodetype=cwf.accept),
        'thesis_review': dict(nodetype=cwf.categorize_retrospective_thesis, name='Thesis Categorization'),
        'thesis_review2': dict(nodetype=cwf.categorize_retrospective_thesis, name='Executive Thesis Categorization'),
        'retro_thesis': dict(nodetype=cwf.review_retrospective_thesis, name="Retrospective Thesis R."),
        'legal_and_patient_review': dict(nodetype=cwf.review_legal_and_patient_data, name="Legal+Patient R."),
        'scientific_review': dict(nodetype=cwf.review_scientific_issues, name="Executive R."),
        'statistical_review': dict(nodetype=cwf.review_statistical_issues, name="Statistical R."),
        'insurance_review': dict(nodetype=cwf.review_insurance_issues, name="Insurance R."),
        'contact_external_reviewer': dict(nodetype=cwf.contact_external_reviewer, name="Contact External Reviewer"),
        'do_external_review': dict(nodetype=cwf.do_external_review, name="External R."),
        'workflow_merge': dict(nodetype=patterns.generic, name="Workflow Merge"),
        'workflow_sync': dict(nodetype=patterns.synchronization, end=True),
        'review_sync': dict(nodetype=patterns.synchronization, name="Review Sync"),
        'scientific_review_complete': dict(nodetype=patterns.generic, name="Scientific R. Complete"),
        'acknowledge_signed_submission_form': dict(nodetype=cwf.acknowledge_signed_submission_form, name="Ack. Signed Submission"),
    }
    
    edges = {
        ('initial_review', 'reject'): dict(guard=cwf.is_accepted, negated=True),
        ('initial_review', 'accept'): dict(guard=cwf.is_accepted),
        ('accept', 'thesis_review2'): dict(guard=cwf.is_marked_as_thesis_by_submitter, negated=True),
        ('accept', 'thesis_review'): dict(guard=cwf.is_marked_as_thesis_by_submitter),
        ('accept', 'acknowledge_signed_submission_form'): dict(),
        ('accept', 'statistical_review'): dict(),
        ('thesis_review', 'thesis_review2'): dict(guard=cwf.is_thesis_and_retrospective, negated=True),
        ('thesis_review', 'retro_thesis'): dict(guard=cwf.is_thesis_and_retrospective),
        ('thesis_review2', 'thesis_review'): dict(guard=cwf.is_thesis_and_retrospective),
        ('thesis_review2', 'not_retrospective_thesis'): dict(guard=cwf.is_thesis_and_retrospective, negated=True),
        ('not_retrospective_thesis', 'legal_and_patient_review'): dict(),
        ('not_retrospective_thesis', 'scientific_review'): dict(),
        ('not_retrospective_thesis', 'insurance_review'): dict(),
        ('scientific_review', 'contact_external_reviewer'): dict(guard=cwf.is_classified_for_external_review),
        ('scientific_review', 'scientific_review_complete'): dict(guard=cwf.is_classified_for_external_review, negated=True),
        ('scientific_review_complete', 'review_sync'): dict(),
        ('contact_external_reviewer', 'do_external_review'): dict(),
        ('do_external_review', 'scientific_review_complete'): dict(),
        ('do_external_review', 'scientific_review'): dict(deadline=True),
        ('statistical_review', 'workflow_sync'): dict(),
        ('insurance_review', 'review_sync'): dict(),
        ('acknowledge_signed_submission_form', 'workflow_sync'): dict(),
        ('review_sync', 'workflow_merge'): dict(),
        ('retro_thesis', 'workflow_merge'): dict(),
        ('workflow_merge', 'workflow_sync'): dict(),
    }
    
    try:
        old_graph = Graph.objects.get(model=Submission, auto_start=True)
    except Graph.MultipleObjectsReturned:
        raise CommandError("There is more than one graph for Submission with auto_start=True.")
    except Graph.DoesNotExist:
        old_graph = None
    
    upgrade = True

    if old_graph:
        upgrade = False
        node_instances = {}
        for name, attrs in nodes.iteritems():
            try:
                node_instances[name] = old_graph.get_node(**attrs)
            except Node.DoesNotExist:
                upgrade = True
                break
        if not upgrade:
            for node_names, attrs in edges.iteritems():
                from_name, to_name = node_names
                try:
                    node_instances[from_name].get_edge(node_instances[to_name], **attrs)
                except Edge.DoesNotExist:
                    upgrade = True
                    break

    if upgrade:
        if old_graph:
            old_graph.auto_start = False
            old_graph.save()
        
        g = Graph.objects.create(model=Submission, auto_start=True)
        node_instances = {}
        for name, attrs in nodes.iteritems():
            node_instances[name] = g.create_node(**attrs)
        for node_names, attrs in edges.iteritems():
            from_name, to_name = node_names
            node_instances[from_name].add_edge(node_instances[to_name], **attrs)

@bootstrap.register()
def auth_groups():
    groups = (
        u'Presenter',
        u'EC-Office',
        u'EC-Meeting Secretary',
        u'EC-Internal Review Group',
        u'EC-Executive Board Group',
        u'EC-Signing Group',
        u'EC-Statistic Group',
        u'EC-Notification Review Group',
        u'EC-Insurance Reviewer',
        u'EC-Thesis Review Group',
        u'EC-Board Member',
        u'External Reviewer',
    )
    
    for group in groups:
        Group.objects.get_or_create(name=group)

@bootstrap.register()
def auth_user_root():
    root, created = User.objects.get_or_create(username='root')
    root.first_name = 'System'
    root.last_name = 'Administrator'
    root.is_staff = True
    root.is_superuser = True
    root.email = 'nobody@example.notexisting.loc'
    root.set_unusable_password()
    root.save()

@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups',))
def auth_user_developers():
    developers = (
        ('wuxxin', u'Felix', u'Erkinger', u'wuxxin@ecsdev.ep3.at'),
        ('mvw', 'Marc', 'van Woerkom', 'mvw@ecsdev.ep3.at'),
        ('emulbreh', u'Johannes', u'Dollinger', 'emulbreh@googlemail.com'),
        ('natano', u'Martin', u'Natano', 'natano@natano.net'),
    )
    
    for dev in developers:
        user, created = User.objects.get_or_create(username=dev[0])
        user.first_name = dev[1]
        user.last_name = dev[2]
        user.email = dev[3]
        user.set_password(dev[4])
        user.save()

@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups',))
def auth_user_testusers():
    testusers = (
        (u'External Reviewer 1', u'External Reviewer'),
        (u'External Reviewer 2', u'External Reviewer'),
        (u'External Reviewer 3', u'External Reviewer'),
        (u'Presenter Testuser 1', u'Presenter'),
        (u'Presenter Testuser 2', u'Presenter'),
        (u'Presenter Testuser 3', u'Presenter'),
        (u'EC-Office Testuser 1', u'EC-Office'),
        (u'EC-Office Testuser 2', u'EC-Office'),
        (u'EC-Office Testuser 3', u'EC-Office'),
        (u'EC-M. Secretary Testuser u', u'EC-Meeting Secretary'),
        (u'Meeting Secretary Testuser 2', u'EC-Meeting Secretary'),
        (u'Meeting Sec. Testuser 3', u'EC-Meeting Secretary'),
        (u'Internal R. Testuser 1', u'EC-Internal Review Group'),
        (u'Internal R. Group Testuser 2', u'EC-Internal Review Group'),
        (u'Internal R. Group Testuser 3', u'EC-Internal Review Group'),
        (u'Ex. Board Testuser 1', u'EC-Executive Board Group'),
        (u'Ex. Board Testuser 2', u'EC-Executive Board Group'),
        (u'Ex. Board Group Testuser 3', u'EC-Executive Board Group'),
        (u'EC-Signing Group Testuser 1', u'EC-Signing Group'),
        (u'EC-Signing Group Testuser 2', u'EC-Signing Group'),
        (u'EC-Signing Group Testuser 3', u'EC-Signing Group'),
        (u'EC-Statistic Group Testuser 1', u'EC-Statistic Group'),
        (u'EC-Statistic Group Testuser 2', u'EC-Statistic Group'),
        (u'EC-Statistic Group Testuser 3', u'EC-Statistic Group'),
        (u'Notification R. Testuser 1', u'EC-Notification Review Group'),
        (u'Notification R. Testuser 2', u'EC-Notification Review Group'),
        (u'Notification R. Testuser 3', u'EC-Notification Review Group'),
        (u'Ins. R. Testuser 1', u'EC-Insurance Reviewer'),
        (u'Ins. Reviewer Testuser 2', u'EC-Insurance Reviewer'),
        (u'Ins. R. Testuser 3', u'EC-Insurance Reviewer'),
        (u'Thesis R. Group Testuser 1', u'EC-Thesis Review Group'),
        (u'Thesis R. Group Testuser 2', u'EC-Thesis Review Group'),
        (u'Thesis R. Group Testuser 3', u'EC-Thesis Review Group'),
        (u'EC-Board Member Testuser 1', u'EC-Board Member'),
        (u'EC-Board Member Testuser 2', u'EC-Board Member'),
        (u'EC-Board Member Testuser 3', u'EC-Board Member'),
        (u'External Reviewer Testuser 1', u'External Reviewer'),
        (u'External Reviewer Testuser 2', u'External Reviewer'),
        (u'External Reviewer Testuser 3', u'External Reviewer'),
    )
    
    for testuser in testusers:
        user, created = User.objects.get_or_create(username=testuser[0])
        user.groups.add(Group.objects.get(name=testuser[1]))

@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups',))
def auth_users():
    board_members = ()
    
    for cat in categories:
        # FIXME: we need a unique constraint on abbrev for this to be idempotent
        medcat, created = MedicalCategory.objects.get_or_create(abbrev=cat[0])
        medcat.name = cat[1]
        medcat.save()
        for u in cat[2]:
            user = User.objects.get(username=u)
            medcat.users.add(user)


