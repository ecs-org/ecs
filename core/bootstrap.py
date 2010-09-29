# -*- coding: utf-8 -*-
import os, datetime, random
from ecs import bootstrap
from ecs.core.models import ExpeditedReviewCategory, Submission, MedicalCategory, EthicsCommission, ChecklistBlueprint, ChecklistQuestion, Investigator, SubmissionForm, Checklist, ChecklistAnswer
from ecs.notifications.models import NotificationType
from ecs.utils.countries.models import Country
from ecs.workflow.models import Graph, Node, Edge
from ecs.workflow import patterns
from django.core.management.base import CommandError
from django.core.management import call_command
from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site


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
                if not created and tpl.last_changed < datetime.datetime.fromtimestamp(os.path.getmtime(path)):
                    tpl.content = content
                    tpl.save()

@bootstrap.register()
def submission_workflow():
    return
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
        ('scripty', u'Ludwig', u'Hammel', 'ludwig.hammel@gmail.com', 'R1kjsd35px' )
    )
    
    for dev in developers:
        user, created = User.objects.get_or_create(username=dev[0])
        user.first_name = dev[1]
        user.last_name = dev[2]
        user.email = dev[3]
        user.set_password(dev[4])
        user.is_staff = True
        user.save()

@bootstrap.register(depends_on=('ecs.core.bootstrap.auth_groups','ecs.core.bootstrap.medical_categories'))
def auth_user_testusers():
    ''' Test User Creation, target to userswitcher'''
    testusers = (
        (u'Presenter', u'Presenter',{}),
        (u'Sponsor', u'Sponsor', {}),
        (u'Investigtor', u'Investigator', {}),
        (u'Office', u'EC-Office', {}),
        (u'Meeting Secretary', u'EC-Meeting Secretary',
            {'internal': True, }),
        (u'Internal Rev', u'EC-Internal Review Group',
            {'internal': True,}),
        (u'Executive', u'EC-Executive Board Group',             
            {'internal': True, 'executive_board_member': True, }),
        (u'Signing', u'EC-Signing Group',                       
            {'internal': True, }),
        (u'Statistic Rev', u'EC-Statistic Group',
            {'internal': True, }),
        (u'Notification Rev', u'EC-Notification Review Group',
            {'internal': True, }),
        (u'Insurance Rev', u'EC-Insurance Reviewer',            
            {'internal': True, }),
        (u'Thesis Rev', u'EC-Thesis Review Group',              
            {'internal': True, 'thesis_review': True}),
        (u'External Reviewer', u'External Reviewer',            
            {'external_review': True, }),
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
                profile.__setattr__(flagname, flagvalue)
            profile.save()
    
    for testuser, medcategories in boardtestusers:
        user, created = User.objects.get_or_create(username=testuser)
        user.groups.add(Group.objects.get(name='EC-Board Member'))
        user.groups.add(Group.objects.get(name="userswitcher_target"))

        profile = user.get_profile()
        profile.board_member = True
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
    }

    for bp_name in questions.keys():
        blueprint = ChecklistBlueprint.objects.get(name=bp_name)
        print blueprint
        #FIXME: there is no unique constraint, so this is not idempotent
        for q in questions[bp_name]:
            cq, created = ChecklistQuestion.objects.get_or_create(text=q, blueprint=blueprint)

@bootstrap.register(depends_on=('ecs.core.bootstrap.checklist_questions', 'ecs.core.bootstrap.medical_categories', 'ecs.core.bootstrap.ethics_commissions'))
def testsubmission():
    submission, created = Submission.objects.get_or_create(ec_number='4321')
    if not created:
        return
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
        'submitter_contact_last_name': u'Univ. Doz. Dr. Ruth Ladenstein',
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
        'study_plan_blind': 0,
        'study_plan_randomized': False,
        'study_plan_cross_over': False,
        'german_consent_info': u'bla bla bla',
        'medtech_departure_from_regulations': u'',
        'german_project_title': u'bla bla bla',
        'submitter_organisation': u'St. Anna Kinderspital',
        'study_plan_multiple_test_correction_algorithm': u'',
        'sponsor_address1': u'Kinderspitalg. 6',
        'invoice_name': u'',
        'sponsor_address2': u'',
        'german_statistical_info': u'bla bla bla',
    }
    
    submission_form = SubmissionForm.objects.create(**submission_form_data)
    submission_form.substance_p_c_t_countries.add(Country.objects.get(iso='AT'))
    submission_form.substance_p_c_t_countries.add(Country.objects.get(iso='DE'))
    submission_form.substance_p_c_t_countries.add(Country.objects.get(iso='US'))
    
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


