# -*- coding: utf-8 -*-
import os, datetime, random
from ecs import bootstrap
from ecs.core.models import DocumentType, NotificationType, ExpeditedReviewCategory, Submission, MedicalCategory, EthicsCommission, ChecklistBlueprint, ChecklistQuestion, Investigator, SubmissionForm, Checklist, ChecklistAnswer, StudyType
from ecs.utils.countries.models import Country
from ecs.workflow.models import Graph, Node, Edge
from ecs.workflow import patterns
from django.core.management.base import CommandError
from django.core.management import call_command
from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site


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
def default_site():
    Site.objects.get_or_create(pk=1)

@bootstrap.register()
def templates(depends_on=('ecs.core.bootstrap.default_site',)):
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

@bootstrap.register()
def ethics_commissions():
    commissions = [{
        'uuid': u'23d805c6b5f14d8b9196a12005fd2961',
        'city': u'Wien',
        'fax': None,
        'chairperson': None,
        'name': u'Ethikkomission der Medizinischen Universit\u00e4t Wien',
        'url': None,
        'email': None,
        'phone': None,
        'address_1': u'Borschkegasse 8b',
        'contactname': None,
        'address_2': u'',
        'zip_code': u'1090',
    }, {
        'uuid': u'7b51f38bde8a4161a0dc34647fc7e654',
        'city': u'Wien',
        'fax': u'(01) 21121-2103',
        'chairperson': u'Doz.Dr.Stefan Kudlacek',
        'name': u'EK KH d. Barmh. Br\u00fcder Wien',
        'url': None,
        'email': u'abteilung.interne@bbwien.at',
        'phone': u'(01) 21121-5075, -293.55',
        'address_1': u'Gro\u00dfe Mohrengasse 9',
        'contactname': None,
        'address_2': u'',
        'zip_code': u'A-1020',
    }, {
        'uuid': u'85dc386061584fbe8549ce4e4d828fbd',
        'city': u'Wien',
        'fax': u'(01) 4000-99-87754, -87755, -87756',
        'chairperson': u'Dr.Karin Spacek',
        'name': u'EK der Stadt Wien gem\u00e4\u00df KAG, AMG und MPG',
        'url': u'http://www.wien.gv.at/ma15/ethikkommission/index.htm',
        'email': u'ik-eth@ma15.wien.gv.at',
        'phone': u'(01) 4000-87754, -87755, -87756',
        'address_1': u'TownTown, Thomas-Klestil-Platz 8',
        'contactname': u'Reinhard Undeutsch',
        'address_2': u'',
        'zip_code': u'A-1030',
    }, {
        'uuid': u'd6a22c635a584521b107481ac18318f6',
        'city': u'Wien',
        'fax': u'(01) 79580-9730',
        'chairperson': u'Mag.Alexander Lang',
        'name': u'EK Forschungsinstitut des Wiener Roten Kreuzes',
        'url': u'www.wrk.at/forschungsinstitut',
        'email': u'forschung@w.roteskreuz.at',
        'phone': u'(01) 79580-1423 oder -1402',
        'address_1': u'Nottendorfer Gasse 21',
        'contactname': u'Fr. Mag.Gabriele Sprengseis',
        'address_2': u'',
        'zip_code': u'A-1030',
    }, {
        'uuid': u'55ae93ec9df04d6abfc8d233ec5ccf8e',
        'city': u'Wien',
        'fax': u'(01) 599 88-4041',
        'chairperson': u'Prim.Dr.Boris Todoroff',
        'name': u'EK KH Barmh.Schwestern, Wien',
        'url': None,
        'email': u'office.wien@bhs.at',
        'phone': u'(01) 59988-2122',
        'address_1': u'Stumpergasse 13',
        'contactname': None,
        'address_2': u'',
        'zip_code': u'A-1060',
    }, {
        'uuid': u'7cd6d52120b3474ba502931b9f60a5f3',
        'city': u'Wien',
        'fax': u'(01) 40114-5707',
        'chairperson': u'Prim.Dr.Dieter Volc',
        'name': u'EK Confraternit\u00e4t-Priv.Klin. Josefstadt und Priv.Klin. D\u00f6bling',
        'url': None,
        'email': u'dieter.volc@pkj.at',
        'phone': u'(01) 40114-99',
        'address_1': u'Skodagasse 32',
        'contactname': None,
        'address_2': u'',
        'zip_code': u'A-1080',
    }, {
        'uuid': u'a641339e597d4d7e8640e4c4e75c38be',
        'city': u'Wien',
        'fax': u'(01) 40400-1690',
        'chairperson': u'Univ.Prof.Dr.Ernst Singer',
        'name': u'EK Med.Universit\u00e4t Wien',
        'url': u'www.meduniwien.ac.at/ethik',
        'email': u'ethik-kom@meduniwien.ac.at',
        'phone': u'(01) 40400-2147, -2248, -2241',
        'address_1': u'Borschkegasse 8b/E 06',
        'contactname': u'Fr. Dr.Christiane Druml',
        'address_2': u'',
        'zip_code': u'A-1090',
    }, {
        'uuid': u'7df9ebaf15434709b09c3def9a6c8769',
        'city': u'Wien',
        'fax': u'(01) 40170-765',
        'chairperson': u'Dr.Roland Lavaulx-Vrecourt',
        'name': u'EK St.Anna Kinderspital',
        'url': u'www.stanna.at',
        'email': u'verwaltungsdirektion@stanna.at',
        'phone': u'(01) 40170-260',
        'address_1': u'Kinderspitalgasse 6',
        'contactname': None,
        'address_2': u'',
        'zip_code': u'A-1090',
    }, {
        'uuid': u'f122f144616541d391fde2dcc761aff4',
        'city': u'Wien',
        'fax': u'(01) 408 4511-17',
        'chairperson': u'Univ.Prof.Dr.Gerhart Hitzenberger',
        'name': u'EK \u00d6sterreichische Arbeitsgemeinschaft f\u00fcr Klinische Pharmakologie',
        'url': u'www.ethikkommission-klinpharm.at',
        'email': u'office@ethikkommission-klinpharm.at',
        'phone': u'(01) 408 4511-26',
        'address_1': u'Kinderspitalgasse 10/15',
        'contactname': None,
        'address_2': u'',
        'zip_code': u'A-1090',
    }, {
        'uuid': u'25b6744780434a3f96a1e43b405d3848',
        'city': u'Wien',
        'fax': None,
        'chairperson': u'Univ.Prof.Dr.Fritz Paschke',
        'name': u'EK Privatkrankenanstalt Rudolfinerhaus',
        'url': None,
        'email': u'w.weissenhofer@rudolfinerhaus.at',
        'phone': u'(01) 360360',
        'address_1': u'Billrothstrasse 78',
        'contactname': u'Univ.Doz.Dr.Werner Weissenhofer',
        'address_2': u'',
        'zip_code': u'A-1090',
    }, {
        'uuid': u'd542994ced34403db841786a1c1ab892',
        'city': u'Wien',
        'fax': u'(01) 68009-9234',
        'chairperson': u'(erreichbar \u00fcber "Kontakt")',
        'name': u'EK Rheuma-Zentrum Wien-Oberlaa',
        'url': None,
        'email': u'office@rhz-oberlaa.at',
        'phone': u'(01) 68009-9231',
        'address_1': u'Kurbadstrasse 10',
        'contactname': u'Fr. Erika Karner',
        'address_2': u'',
        'zip_code': u'A-1100',
    }, {
        'uuid': u'5615dfbaf8c8445d960d1e2cd9c00dc3',
        'city': u'Wien',
        'fax': u'(01) 4865-631-343',
        'chairperson': u'OA Dr.Michael Peintinger',
        'name': u'EK KA des G\u00f6ttlichen Heilandes',
        'url': None,
        'email': u'michael.peintinger@meduniwien.ac.at',
        'phone': u'(01) 4865-631-0',
        'address_1': u'Dornbacher Strasse 20-28',
        'contactname': None,
        'address_2': u'',
        'zip_code': u'A-1170',
    }, {
        'uuid': u'4d3a2d5f138940f293ee87fe6ec1d5b2',
        'city': u'Wien',
        'fax': u'(01) 40422-510',
        'chairperson': u'DDr. Martin Bolz',
        'name': u'EK Evangelisches Krankenhaus',
        'url': None,
        'email': u'b.savic@ekhwien.at',
        'phone': u'(01) 40422-504',
        'address_1': u'Hans-Sachs-Gasse 10-12',
        'contactname': None,
        'address_2': u'',
        'zip_code': u'A-1180',
    }, {
        'uuid': u'8d2950e3a0294f68bde647a54df6d823',
        'city': u'Wien',
        'fax': u'(01) 33111-379',
        'chairperson': u'Dr.Helmut K\u00f6berl',
        'name': u'EK der Allgemeinen Unfallversicherungsanstalt',
        'url': None,
        'email': u'helmut.koeberl@auva.at',
        'phone': u'(01) 33111-458',
        'address_1': u'Adalbert-Stifter-Strasse 65',
        'contactname': None,
        'address_2': u'',
        'zip_code': u'A-1200',
    }, {
        'uuid': u'b17f32f604fa4452b5ff3a2baa9e0704',
        'city': u'St.P\u00f6lten',
        'fax': u'(02742) 9005 -12785',
        'chairperson': u'Mag.Robert Bruckner',
        'name': u'EK des Landes Nieder\u00f6sterreich',
        'url': u'http://www.noel.gv.at/ethikkommission',
        'email': u'post.ethikkommission@noel.gv.at',
        'phone': u'(02742) 9005 -12731, -15669, -15677',
        'address_1': u'c/o Abt. Sanit\u00e4tsrecht u. Krankenanstalten',
        'contactname': u'Fr. Astrid Dana',
        'address_2': u'Landhausplatz 1, Haus 15B',
        'zip_code': u'A-3109',
    }, {
        'uuid': u'6688ce16a3b84d42b1531389e6039891',
        'city': u'Linz',
        'fax': u'(0732) 7676-4418',
        'chairperson': u'Univ.Doz.Dr.Rainer Sch\u00f6fl',
        'name': u'EK KH Elisabethinen',
        'url': u'http://www.elisabethinen.or.at/30000_das_krankenhaus/30702_ethikk_start.htm',
        'email': u'rainer.schoefl@elisabethinen.or.at',
        'phone': u'(0732) 7676-4414',
        'address_1': u'Fadingerstrasse 1',
        'contactname': u'Fr. Sabine Metz',
        'address_2': u'',
        'zip_code': u'A-4010',
    }, {
        'uuid': u'e4dcd05a31ad475ca72dea7b84ef030e',
        'city': u'Linz',
        'fax': u'0732/6921-25904 (Fischer) bzw. 0732/7720-215619 (Drda)',
        'chairperson': u'Univ.Prof.Prim.Dr.Johannes Fischer',
        'name': u'EK des Landes Ober\u00f6sterreich',
        'url': u'http://ooe-ethikkommission.at',
        'email': u'johannes.fischer@gespag.at',
        'phone': u'0732/6921-25900 (Fischer) bzw. 0732/7720-15220 (Drda)',
        'address_1': u'c/o Landesnervenklinik Wagner-Jauregg',
        'contactname': u'Univ.Prof.Prim.Dr.Johannes Fischer bzw. Fr. Dr.Elgin Drda',
        'address_2': u'Wagner-Jauregg Weg 15',
        'zip_code': u'A-4020',
    }, {
        'uuid': u'e269491bb9c040aaad6a5f11df343f38',
        'city': u'Linz',
        'fax': u'(0732) 1099',
        'chairperson': u'Prim.Univ.Prof.Dr.Kurt Lenz',
        'name': u'EK KH Barmh.Br\u00fcder Linz',
        'url': None,
        'email': u'kurt.lenz@bblinz.at',
        'phone': u'(0732) 7897',
        'address_1': u'Seilerst\u00e4tte 2',
        'contactname': None,
        'address_2': u'',
        'zip_code': u'A-4020',
    }, {
        'uuid': u'1cca34032077445d95dabf7802fade28',
        'city': u'Linz',
        'fax': u'(0732) 7677-7865',
        'chairperson': u'Univ.Prof.Dr.Peter Siostrzonek',
        'name': u'EK KH Barmh.Schwestern',
        'url': None,
        'email': u'ethik.linz@bhs.at',
        'phone': u'(0732) 7677-7262',
        'address_1': u'Seilerst\u00e4tte 4',
        'contactname': u'Fr. Hannelore Haunschmidt',
        'address_2': u'',
        'zip_code': u'A-4020',
    }, {
        'uuid': u'39cbb589ef044d27bceb6ee5ac796ae7',
        'city': u'Salzburg',
        'fax': u'(0662) 8042-2929',
        'chairperson': u'Mag.Thomas Russegger',
        'name': u'EK f.d.Bundesland Salzburg',
        'url': u'http://www.salzburg.gv.at/ethikkommission',
        'email': u'ethikkommission@salzburg.gv.at',
        'phone': u'(0662) 8042-2375',
        'address_1': u'Sebastian-Stief-Gasse 2',
        'contactname': u'Fr. Mag.Silvia Peterbauer',
        'address_2': u'',
        'zip_code': u'A-5010',
    }, {
        'uuid': u'280414583b894c809a9baa8134d7fe4b',
        'city': u'Innsbruck',
        'fax': u'(0512) 504-22295',
        'chairperson': u'Univ.Prof.DI Dr.Peter Lukas',
        'name': u'EK Med.Universit\u00e4t Innsbruck',
        'url': u'http://www.i-med.ac.at/ethikkommission',
        'email': u'Ethikkommission@i-med.ac.at',
        'phone': u'(0512) 504-25444, 22293',
        'address_1': u'c/o Gesch\u00e4ftsstelle',
        'contactname': u'Fr. Mag.Karin Pardeller',
        'address_2': u'Innrain 43',
        'zip_code': u'A-6020',
    }, {
        'uuid': u'183881da8200493aa7edd8bebeea75b9',
        'city': u'Bregenz',
        'fax': u'(05574) 58372',
        'chairperson': u'Mag.pharm.Dr.Helmut Grimm',
        'name': u'EK des Landes Vorarlberg',
        'url': u'http://www.ethikkommission-vorarlberg.at',
        'email': u'ethikkomm.vlbg@bregenznet.at',
        'phone': u'(05574) 58372',
        'address_1': u'c/o Gesch\u00e4ftsstelle',
        'contactname': u'Fr. M.Achberger',
        'address_2': u'Rathausstrasse 15',
        'zip_code': u'A-6900',
    }, {
        'uuid': u'95821eba88f34b2195f96e747d7f6b16',
        'city': u'Eisenstadt',
        'fax': u'05 7979 5306',
        'chairperson': u'PDir.DGKS Renate Peischl, MAS',
        'name': u'EK des Landes Burgenland gem\u00e4\u00df KAG, AMG und MPG',
        'url': u'http://www.krages.at/Ethikkommission.31.0.html',
        'email': u'renate.peischl@krages.at',
        'phone': u'05 7979 30015',
        'address_1': u'Josef-Hyrtl-Platz 4',
        'contactname': None,
        'address_2': u'',
        'zip_code': u'A-7000',
    }, {
        'uuid': u'6e7cfab5f8cd40df83c9de4fac9bb20f',
        'city': u'Graz',
        'fax': u'(0316) 877-3555, -805840',
        'chairperson': u'HR Dr.Odo Feenstra',
        'name': u'EK gem\u00e4\u00df AMG und MPG',
        'url': u'http://www.verwaltung.steiermark.at/cms/ziel/442986/DE/',
        'email': u'brigitte.jauernik@stmk.gv.at',
        'phone': u'(0316) 877-5840',
        'address_1': u'c/o Amt d. Stmk.LR, FA8B - Gesundheitswesen',
        'contactname': u'Fr. Dr.Brigitte Jauernik',
        'address_2': u'Friedrichgasse 9',
        'zip_code': u'A-8010',
    }, {
        'uuid': u'75b5a9714f354a5b842aa01029148036',
        'city': u'Graz',
        'fax': None,
        'chairperson': u'Prim.Univ.Doz.Dr.G\u00fcnther Weber',
        'name': u'EK KH Barmh.Br\u00fcder - Marschallgasse',
        'url': None,
        'email': u'guenther.weber@bbgraz.at',
        'phone': u'(0316) 7067-0',
        'address_1': u'Marschallgasse 12',
        'contactname': None,
        'address_2': u'',
        'zip_code': u'A-8020',
    }, {
        'uuid': u'9287fb0878b94f9f9d90b5582d1cefca',
        'city': u'Graz',
        'fax': None,
        'chairperson': u'Prof.Dr.Peter K\u00f6ltringer',
        'name': u'EK KH Barmh.Br\u00fcder - Eggenberg',
        'url': None,
        'email': u'peter.koeltringer@bbegg.at',
        'phone': u'(0316) 5989-0',
        'address_1': u'Bergstrasse 27',
        'contactname': None,
        'address_2': u'',
        'zip_code': u'A-8020',
    }, {
        'uuid': u'e17ee744e4e840778f316cf3f79de6b4',
        'city': u'Graz',
        'fax': u'(0316) 385-4348',
        'chairperson': u'Univ.Prof.DI.Dr.Peter H. Rehak',
        'name': u'EK Med.Universit\u00e4t Graz',
        'url': u'www.meduni-graz.at/ethikkommission/Graz/index.htm',
        'email': u'ethikkommission@medunigraz.at',
        'phone': u'(0316) 385-3928, -2817',
        'address_1': u'Auenbruggerplatz 2',
        'contactname': u'Fr. Mag.Andrea Berghofer',
        'address_2': u'',
        'zip_code': u'A-8036',
    }, {
        'uuid': u'ec9f179a52a04a7aa52446232c3fd4bd',
        'city': u'Klagenfurt',
        'fax': u'(0463) 538-23184',
        'chairperson': u'OA Dr.Gerhard Kober',
        'name': u'EK des Landes K\u00e4rnten',
        'url': u'http://www.ethikkommission-kaernten.at',
        'email': u'Ethik@lkh-klu.at',
        'phone': u'(0463) 538-29100',
        'address_1': u'c/o LKH Klagenfurt',
        'contactname': u'Fr. Yvonne Wernig',
        'address_2': u'St.-Veiter-Strasse 45-47',
        'zip_code': u'A-9020',
    }]

    for comm in commissions:
        ec, created = EthicsCommission.objects.get_or_create(uuid=comm['uuid'])
        for key in comm.keys():
            setattr(ec, key, comm[key])
        ec.save()

@bootstrap.register()
def checklist_blueprints():
    blueprints = (
        u'Statistik',
    )
    
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
    }

    for bp_name in questions.keys():
        blueprint = ChecklistBlueprint.objects.get(name=bp_name)
        print blueprint
        #FIXME: there is no unique constraint, so this is not idempotent
        for q in questions[bp_name]:
            cq, created = ChecklistQuestion.objects.get_or_create(text=q, blueprint=blueprint)

@bootstrap.register()
def study_types():
    types = ['AMG', 'MPG']
    for type in types:
        StudyType.objects.get_or_create(name=type)

@bootstrap.register(depends_on=('ecs.core.bootstrap.checklist_questions', 'ecs.core.bootstrap.medical_categories', 'ecs.core.bootstrap.ethics_commissions', 'ecs.core.bootstrap.auth_user_root'))
def testsubmission():
    submission, created = Submission.objects.get_or_create(ec_number='4321')
    submission.medical_categories.add(MedicalCategory.objects.get(abbrev='Kinder'))
    
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
        'submitter_name': u'Univ. Doz. Dr. Ruth Ladenstein',
        'submitter_is_authorized_by_sponsor': False,
        'medtech_manufacturer': u'',
        'subject_planned_total_duration': u'8 months',
        'project_type_medical_device_with_ce': False,
        'submitter_is_sponsor': False,
        'german_summary': u'bla bla bla',
        'insurance_contract_number': u'WF-07218230-8',
        'study_plan_power': u'0.80',
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
        'sponsor_contactname': None,
        'study_plan_dataprotection_reason': u'',
        'medtech_certified_for_exact_indications': False,
        'sponsor_city': u'Wien',
        'medtech_manual_included': False,
        'submitter_agrees_to_publishing': True,
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
        'study_plan_randomized': False,
        'study_plan_cross_over': False,
        'german_consent_info': u'bla bla bla',
        'medtech_departure_from_regulations': u'',
        'german_project_title': u'bla bla bla',
        'submitter_organisation': u'St. Anna Kinderspital',
        'study_plan_multiple_test_correction_algorithm': u'',
        'sponsor_address1': u'Kinderspitalg. 6',
        'invoice_name': u'',
        'invoice_contactname': None,
        'sponsor_address2': u'',
        'german_statistical_info': u'bla bla bla',
    }
    
    
    
    submission_form = SubmissionForm.objects.create(**submission_form_data)
    submission_form.substance_p_c_t_countries.add(Country.objects.get(iso='AT'))
    submission_form.substance_p_c_t_countries.add(Country.objects.get(iso='DE'))
    submission_form.substance_p_c_t_countries.add(Country.objects.get(iso='US'))
    
    Investigator.objects.create(
        name=u'Univ. Doz. Dr. Ruth Ladenstein',
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


