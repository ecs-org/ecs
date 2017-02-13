import datetime
import traceback
import re
import collections
from collections import OrderedDict

from diff_match_patch import diff_match_patch
from django_countries import countries

from django.utils.translation import ugettext as _
from django.utils.encoding import force_text
from django.utils import timezone
from django.db import models
from django.db.models import Manager, QuerySet
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.utils.html import escape

from ecs.core.models import SubmissionForm, Investigator, EthicsCommission, \
    Measure, NonTestedUsedDrug, ParticipatingCenterNonSubject, \
    ForeignParticipatingCenter, InvestigatorEmployee
from ecs.documents.models import Document
from ecs.utils.viewutils import render_html
from ecs.core import paper_forms
from ecs.users.utils import get_full_name, get_current_user


DATETIME_FORMAT = '%d.%m.%Y %H:%M'
DATE_FORMAT = '%d.%m.%Y'


def words_to_chars(text1, text2):
    words = []
    word_map = {}

    def translate(text):
        chars = []
        boundaries = [m.start() for m in re.finditer(r'[ \t\n]', text)]
        for word_start, word_end in \
                zip([-1] + boundaries, boundaries + [len(text) - 1]):
            word = text[word_start+1:word_end+1]
            if word not in word_map:
                words.append(word)
                word_map[word] = len(words) - 1
            chars.append(chr(word_map[word]))
        return ''.join(chars)

    chars1 = translate(text1)
    chars2 = translate(text2)
    return (chars1, chars2, words)


def word_diff(a, b):
    dmp = diff_match_patch()
    a, b, wordArray = words_to_chars(a, b)
    diff = dmp.diff_main(a, b, checklines=False)
    dmp.diff_cleanupSemantic(diff)
    dmp.diff_charsToLines(diff, wordArray)
    return diff


class DiffNode(object):
    def __init__(self, old, new, identity=None, ignore_old=False, ignore_new=False):
        self.old = old
        self.new = new
        self.identity = identity
        self.ignore_old = ignore_old
        self.ignore_new = ignore_new

    def html(self, plain=False):
        raise NotImplementedError

class TextDiffNode(DiffNode):
    def html(self, plain=False):
        diff = word_diff(self.old, self.new)
        result = []
        for op, bit in diff:
            if op:
                result.append('<span class="%s">%s</span>' % ('inserted' if op > 0 else 'deleted', bit))
            else:
                result.append(bit)
        return "".join(result)


class AtomicDiffNode(DiffNode):
    def format(self, val):
        return str(val)

    def html(self, plain=False):
        result = []
        if not self.ignore_old:
            old = self.old
            if isinstance(old, collections.Callable):
                old = old(plainhtml=plain)
            result.append('<span class="deleted">- %s</span>' % force_text(old))
        if not self.ignore_new:
            new = self.new
            if isinstance(new, collections.Callable):
                new = new(plainhtml=plain)
            result.append('<span class="inserted">+ %s</span>' % force_text(new))
        return '<div class="atomic">%s</div>' % ''.join(result)
        


class ModelDiffNode(DiffNode):
    def __init__(self, old, new, field_diffs, **kwargs):
        super().__init__(old, new, **kwargs)
        self.field_diffs = field_diffs
        
    def __bool__(self):
        return bool(self.field_diffs)
        
    def __getitem__(self, label):
        return self.field_diffs[label]
    
    def html(self, plain=False):
        try:
            result = []
            for label, node in self.field_diffs.items():
                result.append('<div class="field">%s: %s</div>' % (label, node.html(plain=plain)))
            result = "\n".join(result)
            if self.identity:
                result = '<span class="title">%s</span>\n%s' % (self.identity, result)
            return result
        except Exception as e:
            traceback.print_exc()


class ListDiffNode(DiffNode):
    css_map = {
        '+': 'inserted',
        '-': 'deleted',
        '~': 'changed',
    }
    
    def __init__(self, old, new, **kwargs):
        super().__init__(old, new, **kwargs)
        self._prepare()
        
    def _prepare(self):
        differ = None
        if self.old:
            differ = _differs[self.old[0].__class__]
        elif self.new:
            differ = _differs[self.new[0].__class__]
        else:
            self.diffs = []
            return

        diffs = []
        for old in self.old:
            omf = [getattr(old, f) for f in differ.match_fields]
            for new in self.new:
                nmf = [getattr(new, f) for f in differ.match_fields]
                if omf == nmf:
                    self.new.remove(new)
                    break
            else:
                diffs.append(('-', diff_model_instances(old, None, ignore_new=True)))
                continue
            item_diff = diff_model_instances(old, new, ignore_old=self.ignore_old, ignore_new=self.ignore_new)
            if item_diff:
                diffs.append(('~', item_diff))

        diffs += [('+', diff_model_instances(None, new, ignore_old=True)) for new in self.new]
        
        diffs.sort(key=lambda d: d[1].identity)
        self.diffs = diffs
        
    def __bool__(self):
        return bool(self.diffs)
    
    def html(self, plain=False):
        result = []
        for op, diff in self.diffs:
            html = ''
            if not op == '~':
                html = str(op) + ' '
            html += diff.html(plain=plain)
            result.append('<div class="item %s">%s</div>' % (self.css_map[op], html))
        return '\n'.join(result)


class DocumentListDiffNode(ListDiffNode):
    def __init__(self, old, new, old_sf=None, new_sf=None, **kwargs):
        self.old_sf = old_sf
        self.new_sf = new_sf
        super().__init__(old, new, **kwargs)

    def _prepare(self):
        old = set(self.old)
        new = set(self.new)
        changed = sorted(old ^ new,
            key=lambda d: (d.doctype.identifier, d.date, d.name))

        self.diffs = []

        old_differ = DocumentDiffer(submission_form=self.old_sf)
        new_differ = DocumentDiffer(submission_form=self.new_sf)

        for doc in changed:
            if doc in new:
                self.diffs.append(
                    ('+', new_differ.diff(None, doc, ignore_old=True)))
            elif doc in old:
                self.diffs.append(
                    ('-', old_differ.diff(doc, None, ignore_new=True)))

    def html(self, plain=False):
        return "\n".join(d.html(plain=plain) for op, d in self.diffs)


class CountryListDiffNode(DiffNode):
    def __bool__(self):
        return set(self.old) != set(self.new)

    def html(self, plain=False):
        old = '\n'.join(sorted(str(countries.name(c)) for c in self.old))
        new = '\n'.join(sorted(str(countries.name(c)) for c in self.new))

        dmp = diff_match_patch()
        a, b, lineArray = dmp.diff_linesToChars(old, new)
        diff = dmp.diff_main(a, b, checklines=False)
        dmp.diff_cleanupSemantic(diff)
        dmp.diff_charsToLines(diff, lineArray)

        result = []
        for op, country in diff:
            if op:
                result.append('<div class="{}">{}</div>'.format(
                    'inserted' if op > 0 else 'deleted', escape(country)))
            else:
                result.append('<div>{}</div>'.format(escape(country)))
        return '\n'.join(result)


def _render_value(val):
    if val is None:
        return _('No Information')
    elif val is True:
        return _('Yes')
    elif val is False:
        return _('No')
    elif isinstance(val, int):
        return str(val)
    elif isinstance(val, datetime.date):
        return val.strftime(DATE_FORMAT)
    elif isinstance(val, datetime.datetime):
        return timezone.localtime(val).strftime(DATETIME_FORMAT)
    return str(val)


class ModelDiffer(object):
    def __init__(self, model=None, fields=None, match_fields=None,
        identify=None, label_map=None):

        if model:
            self.model = model
        self.fields = fields
        self.match_fields = match_fields
        self.identify = identify
        self.label_map = label_map or {}

    def diff_field(self, name, old, new, **kwargs):
        old_val = getattr(old, name, None)
        new_val = getattr(new, name, None)
        
        if old_val == new_val:
            return None
        
        try:
            field = self.model._meta.get_field(name)
        except models.FieldDoesNotExist:
            field = None
        
        if isinstance(field, models.ForeignKey):
            return diff_model_instances(old_val, new_val, model=field.rel.to, **kwargs)
        elif isinstance(new_val, (Manager, QuerySet)) or isinstance(old_val, (Manager, QuerySet)):
            old_val = list(old_val.all()) if old else []
            new_val = list(new_val.all()) if new else []
            if not old_val and not new_val:
                return None
            return ListDiffNode(old_val, new_val, **kwargs)
        elif field is not None and field.choices:
            old_val = str(dict(field.choices)[old_val]) if old_val else _('No Information')
            new_val = str(dict(field.choices)[new_val]) if new_val else _('No Information')
            return AtomicDiffNode(old_val, new_val, **kwargs)
        elif isinstance(field, (models.CharField, models.TextField)) and old_val and new_val:
            return TextDiffNode(old_val, new_val, **kwargs)
        else:
            return AtomicDiffNode(_render_value(old_val), _render_value(new_val), **kwargs)
            
    def diff(self, old, new, **kwargs):
        d = []
        for name in self.fields:
            field_info = paper_forms.get_field_info(self.model, name, None)

            if name in self.label_map:
                label = self.label_map[name]
            elif field_info is not None:
                label = force_text(field_info.label)
                if field_info.number:
                    label = "%s %s" % (field_info.number, label)
            else:
                label = name
            field_diff = self.diff_field(name, old, new, **kwargs)
            if field_diff:
                d.append((label, field_diff))
        identity = None
        if self.identify:
            identity = getattr(new or old, self.identify)
        return ModelDiffNode(old, new, OrderedDict(d), identity=identity)


class AtomicModelDiffer(ModelDiffer):
    def format(self, obj):
        return str(obj)

    def diff(self, old, new, **kwargs):
        if old == new:
            return
        old = self.format(old) if old is not None else _('No Information')
        new = self.format(new) if new is not None else _('No Information')
        return AtomicDiffNode(old, new, **kwargs)


class DocumentDiffer(AtomicModelDiffer):
    model = Document

    def __init__(self, submission_form=None):
        super().__init__()
        self.submission_form = submission_form

    def format(self, doc):
        def _render(plainhtml=False):
            data = {
                'doc': doc,
                'plainhtml': plainhtml,
                'submission_form': self.submission_form,
                'user': get_current_user(),
            }
            return render_html(HttpRequest(), 'submissions/diff/document.html', data)
        return _render


class UserDiffer(AtomicModelDiffer):
    model = User

    def format(self, user):
        return '{0} <{1}>'.format(get_full_name(user), user.email)


class SubmissionFormDiffer(ModelDiffer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name in self.fields:
            if name.startswith('invoice_'):
                fi = paper_forms.get_field_info(self.model, name, None)
                self.label_map[name] = '{}: {} {}'.format(
                    _('invoice recipient'), fi.number, fi.label)
            elif name.startswith('sponsor_'):
                fi = paper_forms.get_field_info(self.model, name, None)
                self.label_map[name] = '{}: {} {}'.format(
                    _('sponsor'), fi.number, fi.label)

    def diff_field(self, name, old, new, **kwargs):
        if name in ('substance_registered_in_countries', 'substance_p_c_t_countries'):
            old_val = getattr(old, name, None)
            new_val = getattr(new, name, None)
            return CountryListDiffNode(old_val, new_val, **kwargs)
        elif name == 'documents':
            old_val = old.documents.select_related('doctype') if old else None
            new_val = new.documents.select_related('doctype') if new else None
            return DocumentListDiffNode(old_val, new_val, **kwargs,
                old_sf=old, new_sf=new)
        else:
            return super().diff_field(name, old, new, **kwargs)


_differs = {
    SubmissionForm: SubmissionFormDiffer(SubmissionForm,
        fields = (
            'documents', 'project_title', 'eudract_number', 'sponsor_name',
            'sponsor_contact_gender', 'sponsor_contact_title',
            'sponsor_contact_first_name', 'sponsor_contact_last_name',
            'sponsor_address', 'sponsor_zip_code', 'sponsor_city',
            'sponsor_phone', 'sponsor_fax', 'sponsor_email', 'sponsor_uid',
            'invoice_name', 'invoice_contact_gender', 'invoice_contact_title',
            'invoice_contact_first_name', 'invoice_contact_last_name',
            'invoice_address', 'invoice_zip_code', 'invoice_city',
            'invoice_phone', 'invoice_fax', 'invoice_email', 'invoice_uid',
            'project_type_non_reg_drug', 'project_type_reg_drug',
            'project_type_reg_drug_within_indication',
            'project_type_reg_drug_not_within_indication',
            'project_type_medical_method', 'project_type_medical_device',
            'project_type_medical_device_with_ce',
            'project_type_medical_device_without_ce',
            'project_type_medical_device_performance_evaluation',
            'project_type_basic_research', 'project_type_genetic_study',
            'project_type_misc', 'project_type_education_context',
            'project_type_register', 'project_type_biobank',
            'project_type_retrospective', 'project_type_questionnaire',
            'project_type_psychological_study', 'project_type_nursing_study',
            'project_type_non_interventional_study',
            'project_type_gender_medicine', 'specialism',
            'pharma_checked_substance', 'pharma_reference_substance',
            'medtech_checked_product', 'medtech_reference_substance',
            'clinical_phase', 'already_voted', 'subject_count',
            'subject_minage', 'subject_maxage', 'subject_males',
            'subject_females_childbearing', 'subject_females',
            'subject_childbearing', 'subject_noncompetents', 'subject_duration',
            'subject_duration_active', 'subject_duration_controls',
            'subject_planned_total_duration', 'submission_type',
            'substance_registered_in_countries',
            'substance_preexisting_clinical_tries', 'substance_p_c_t_countries',
            'substance_p_c_t_phase', 'substance_p_c_t_period',
            'substance_p_c_t_application_type', 'substance_p_c_t_gcp_rules',
            'substance_p_c_t_final_report', 'medtech_product_name',
            'medtech_manufacturer', 'medtech_certified_for_exact_indications',
            'medtech_certified_for_other_indications', 'medtech_ce_symbol',
            'medtech_manual_included', 'medtech_technical_safety_regulations',
            'medtech_departure_from_regulations', 'insurance_not_required',
            'insurance_name', 'insurance_address', 'insurance_phone',
            'insurance_contract_number', 'insurance_validity',
            'additional_therapy_info', 'german_project_title', 'german_summary',
            'german_preclinical_results', 'german_primary_hypothesis',
            'german_inclusion_exclusion_crit', 'german_ethical_info',
            'german_protected_subjects_info', 'german_recruitment_info',
            'german_consent_info', 'german_risks_info', 'german_benefits_info',
            'german_relationship_info', 'german_concurrent_study_info',
            'german_sideeffects_info', 'german_statistical_info',
            'german_dataprotection_info', 'german_aftercare_info',
            'german_payment_info', 'german_abort_info',
            'german_dataaccess_info', 'german_financing_info',
            'german_additional_info', 'study_plan_blind', 'study_plan_open',
            'study_plan_randomized', 'study_plan_parallelgroups',
            'is_monocentric', 'study_plan_single_blind',
            'study_plan_controlled', 'study_plan_cross_over', 'is_multicentric',
            'study_plan_double_blind', 'study_plan_placebo',
            'study_plan_factorized', 'study_plan_pilot_project',
            'study_plan_observer_blinded', 'study_plan_equivalence_testing',
            'study_plan_misc', 'study_plan_number_of_groups',
            'study_plan_stratification', 'study_plan_sample_frequency',
            'study_plan_primary_objectives', 'study_plan_null_hypothesis',
            'study_plan_alternative_hypothesis',
            'study_plan_secondary_objectives', 'study_plan_alpha',
            'study_plan_alpha_sided', 'study_plan_power',
            'study_plan_statalgorithm', 'study_plan_multiple_test',
            'study_plan_multiple_test_correction_algorithm',
            'study_plan_dropout_ratio',
            'study_plan_population_intention_to_treat',
            'study_plan_population_per_protocol',
            'study_plan_interim_evaluation', 'study_plan_abort_crit',
            'study_plan_planned_statalgorithm',
            'study_plan_dataquality_checking', 'study_plan_datamanagement',
            'study_plan_biometric_planning',
            'study_plan_statistics_implementation',
            'study_plan_dataprotection_choice',
            'study_plan_dataprotection_reason', 'study_plan_dataprotection_dvr',
            'study_plan_dataprotection_anonalgoritm',
            'submitter_contact_gender', 'submitter_contact_title',
            'submitter_contact_first_name', 'submitter_contact_last_name',
            'submitter_email', 'submitter_organisation', 'submitter_jobtitle',
            'submitter_is_coordinator', 'submitter_is_main_investigator',
            'submitter_is_sponsor', 'submitter_is_authorized_by_sponsor',
            'participatingcenternonsubject_set',
            'foreignparticipatingcenter_set', 'investigators', 'measures',
            'nontesteduseddrug_set',
        ),
        label_map=dict([
            ('participatingcenternonsubject_set', _('centers (non subject)')),
            ('foreignparticipatingcenter_set', _('centers abroad')),
            ('investigators', _('centers (subject)')),
            ('measures', _('Studienbezogen/Routinemäßig durchzuführende Therapie und Diagnostik')),
            ('nontesteduseddrug_set',
                _('Im Rahmen der Studie verabreichte Medikamente, deren Wirksamkeit und/oder Sicherheit nicht Gegenstand der Prüfung sind')),
            ('documents', _('Dokumente')),
        ]),
    ),
    Investigator: ModelDiffer(Investigator,
        fields=(
            'organisation', 'ethics_commission', 'main', 'contact_gender',
            'contact_title', 'contact_first_name', 'contact_last_name', 'phone',
            'mobile', 'fax', 'email', 'jus_practicandi', 'specialist',
            'certified', 'subject_count', 'user', 'employees',
        ),
        match_fields=('organisation', 'ethics_commission'),
        identify='organisation',
        label_map={
            'employees': _('Mitarbeiter'),
        }
    ),
    InvestigatorEmployee: ModelDiffer(InvestigatorEmployee,
        fields=('sex', 'title', 'firstname', 'surname', 'organisation'),
        match_fields=('firstname', 'surname'),
        identify='full_name',
    ),
    Measure: ModelDiffer(Measure, 
        fields=('category', 'type', 'count', 'period', 'total'),
        match_fields=('category', 'type'),
        identify='type',
    ),
    NonTestedUsedDrug: ModelDiffer(NonTestedUsedDrug,
        fields=('generic_name', 'preparation_form', 'dosage'),
        match_fields=('generic_name', 'preparation_form'),
        identify='generic_name',
    ),
    ParticipatingCenterNonSubject: ModelDiffer(ParticipatingCenterNonSubject,
        fields=('name', 'ethics_commission', 'investigator_name'),
        match_fields=('name', 'ethics_commission'),
        identify='name',
    ),
    ForeignParticipatingCenter: ModelDiffer(ForeignParticipatingCenter,
        fields=('name', 'investigator_name'),
        match_fields=('name',),
        identify='name',
    ),
    EthicsCommission: AtomicModelDiffer(),
    User: UserDiffer(),
}

def diff_model_instances(old, new, model=None, ignore_old=False, ignore_new=False):
    if not model:
        if old:
            model = old.__class__
        elif new:
            model = new.__class__
        else:
            return []
    return _differs[model].diff(old, new, ignore_old=ignore_old, ignore_new=ignore_new)
    

def diff_submission_forms(old_submission_form, new_submission_form):
    assert(old_submission_form.submission == new_submission_form.submission)
    return diff_model_instances(old_submission_form, new_submission_form)
