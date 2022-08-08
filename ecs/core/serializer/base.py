import json
import zipfile, os, datetime
from tempfile import TemporaryFile
from uuid import uuid4
from collections import OrderedDict

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField

from ecs.core.models import (
    SubmissionForm, Submission, EthicsCommission, Investigator,
    InvestigatorEmployee, Measure, ParticipatingCenterNonSubject,
    ForeignParticipatingCenter, NonTestedUsedDrug,
)
from ecs.documents.models import Document, DocumentType
from ecs.core.paper_forms import get_field_info

CURRENT_SERIALIZER_VERSION = '1.4'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S+01:00'
DATE_FORMAT = '%Y-%m-%d'
DATA_JSON_NAME = 'data.json'


CHANGELOG = (
    ('*', '0.1'),
    ('+', SubmissionForm, 'project_type_nursing_study', False),
    ('*', '0.2'),
    ('+', SubmissionForm, 'study_plan_multiple_test', False),
    ('+', SubmissionForm, 'study_plan_multiple_test', False),
    ('+', SubmissionForm, 'study_plan_interim_evaluation', False),
    ('+', SubmissionForm, 'study_plan_dataprotection_choice', 'non-personal'),
    ('*', '0.3'),
    ('+', SubmissionForm, 'sponsor_uid_verified_level1', None),
    ('+', SubmissionForm, 'sponsor_uid_verified_level2', None),
    ('*', '0.4'),
    ('-', SubmissionForm, 'sponsor_uid_verified_level1', None),
    ('-', SubmissionForm, 'sponsor_uid_verified_level2', None),
    ('-', SubmissionForm, 'invoice_uid_verified_level1', None),
    ('-', SubmissionForm, 'invoice_uid_verified_level2', None),
    ('+', SubmissionForm, 'sponsor_uid', None),
    ('*', '0.5'),
    ('+', SubmissionForm, 'insurance_not_required', False),
    ('*', '0.6'),
    ('+', SubmissionForm, 'external_reviewer_suggestions', 'nicht zutreffend'),
    ('*', '0.7'),
    ('+', SubmissionForm, 'project_type_non_interventional_study', False),
    ('+', SubmissionForm, 'project_type_gender_medicine', False),
    ('*', '0.8'),
    ('-', SubmissionForm, 'external_reviewer_suggestions', 'nicht zutreffend'),
    ('*', '0.9'),
    ('-', SubmissionForm, 'invoice', None),
    ('*', '1.0'),
    ('-', SubmissionForm, 'protocol_number', 'unbekannt'),
    ('*', '1.1'),
    ('+', SubmissionForm, 'study_plan_alpha_sided', None),
    ('*', '1.2'),
    ('-', SubmissionForm, 'sponsor_agrees_to_publishing', True),
    ('*', '1.3'),
    ('+', SubmissionForm, 'is_old_medtech', True),
    ('*', '1.4'),
)

class FieldDocs(object):
    value = True

    def __init__(self, model=None, field=None, choices=None):
        self.model = model
        if isinstance(field, ArrayField):
            self.field = field.base_field
            self.array = True
        else:
            self.field = field
            self.array = False
        self._choices = choices

    def json_type(self):
        if isinstance(self.field, models.BooleanField):
            return "BOOLEAN"
        elif isinstance(self.field, models.IntegerField):
            return "INTEGER"
        elif isinstance(self.field, (models.FloatField, models.DecimalField)):
            return "FLOAT"
        else:
            return "STRING"
            
    def constraints(self):
        c = []
        if isinstance(self.field, models.DateTimeField):
            c.append(
                "RFC 3339 with timezone UTC+1 (e.g. 2010-07-14T16:04:35+01:00)")
        elif isinstance(self.field, models.DateField):
            c.append("ISO 8601 with timezone UTC+1 (e.g. 2010-07-14)")
        elif isinstance(self.field, models.CharField):
            c.append("max. {} characters".format(self.field.max_length))
        elif isinstance(self.field, models.FileField):
            c.append("valid internal zip file path")
        if self.field and self.field.null:
            c.append("may be null")
        return c

    def choices(self):
        if self._choices:
            cs = self._choices
        elif self.field:
            cs = self.field.choices
        if cs:
            return [(json.dumps(k), v) for k, v in cs]
            
    def paperform_info(self):
        if self.field:
            return get_field_info(self.model, self.field.name)


class ModelSerializer(object):
    exclude = ('id',)
    groups = ()
    follow = ()
    fields = ()

    def __init__(self, model, groups=None, exclude=None, follow=None, fields=None):
        self.model = model
        if groups:
            self.groups = groups
        if exclude:
            self.exclude = exclude
        if follow:
            self.follow = follow
        if fields:
            self.fields = fields

    def is_field_obsolete(self, field, version):
        version_index = CHANGELOG.index(('*', version))

        for entry in CHANGELOG[-1:version_index:-1]:
            if entry[0] == '+' and entry[1] == self.model and entry[2] == field:
                return False
            if entry[0] == '-' and entry[1] == self.model and entry[2] == field:
                return True

        return False

    def is_field_coming(self, field, version):
        version_index = CHANGELOG.index(('*', version))

        for entry in CHANGELOG[-1:version_index:-1]:
            if entry[0] == '+' and entry[1] == self.model and entry[2] == field:
                return True
            if entry[0] == '-' and entry[1] == self.model and entry[2] == field:
                return False


        return False

    def get_default_for_coming_field(self, field, version):
        version_index = CHANGELOG.index(('*', version))

        for entry in CHANGELOG[-1:version_index:-1]:
            if entry[0] == '+' and entry[1] == self.model and entry[2] == field:
                return entry[3]

    def get_field_names(self):
        names = set(f.name for f in self.model._meta.fields if f.name not in self.exclude)
        if self.fields:
            names = names.intersection(self.fields)
        return names.union(self.follow)
        
    def split_prefix(self, name):
        prefix, key = None, name
        for group in self.groups:
            if name.startswith(group):
                prefix, key = group, name[len(group)+1:]
                break
        return prefix, key
        
    def dump_field(self, fieldname, val, zf, obj):
        if val is None or isinstance(val, (bool, str, int, list, datetime.datetime, datetime.date)):
            return val
        if hasattr(val, 'all') and hasattr(val, 'count'):
            try:
                result = []
                for x in val.all():
                    result.append(dump_model_instance(x, zf))
                return result
            except ValueError as e:
                raise ValueError("cannot dump {}.{}: {}".format(
                    self.model.__name__, fieldname, e))
        
        field = self.model._meta.get_field(fieldname)

        if isinstance(field, models.ForeignKey):
            return dump_model_instance(val, zf)
        elif isinstance(field, models.FileField):
            name, ext = os.path.splitext(val.name)
            zip_name = 'attachments/{}{}'.format(uuid4(), ext)
            zf.write(val.path, zip_name)
            return zip_name
        else:
            raise ValueError(
                "cannot serialize objects of type {}".format(type(val)))
        
        return val

    def dump(self, obj, zf):
        d = {}
        for name in self.get_field_names():
            prefix, key = self.split_prefix(name)
            data = self.dump_field(name, getattr(obj, name), zf, obj)
            if prefix:
                d.setdefault(prefix, {})
                d[prefix][key] = data
            else:
                d[name] = data
        return d
        
    def load_many(self, model, val, zf, version, commit=True):
        result = []
        for data in val:
            result.append(load_model_instance(
                model, data, zf, version, commit=commit))
        return result
        
    def load_field(self, fieldname, val, zf, version):
        if val is None:
            return val, False
        try:
            field = self.model._meta.get_field(fieldname)
        except models.fields.FieldDoesNotExist:
            field = None
        deferr = False
        if field:
            if isinstance(field, models.DateTimeField):
                val = timezone.make_aware(
                    datetime.datetime.strptime(val, DATETIME_FORMAT),
                    timezone.utc)
            elif isinstance(field, models.DateField):
                val = datetime.date.strptime(val, DATE_FORMAT)
            elif isinstance(field, models.ManyToManyField):
                val = self.load_many(field.related_model, val, zf, version)
                deferr = True
            elif isinstance(field, models.ManyToOneRel):
                val = self.load_many(field.related_model, val, zf, version,
                    commit=False)
                deferr = True
            elif isinstance(field, models.ForeignKey):
                val = load_model_instance(field.rel.to, val, zf, version)
            elif isinstance(field, GenericRelation):
                val = self.load_many(field.rel.to, val, zf, version,
                    commit=False)
                deferr = True
        elif isinstance(val, list):
            rel_model = getattr(self.model, fieldname).related.related_model
            val = self.load_many(rel_model, val, zf, version, commit=False)
            deferr = True
        return val, deferr
        
    def load(self, data, zf, version, commit=True):
        deferred = []
        fields = {}
        obj = self.model()
        for name in self.get_field_names():
            prefix, key = self.split_prefix(name)
            if self.is_field_obsolete(name, version):
                continue
            elif self.is_field_coming(name, version):
                val = self.get_default_for_coming_field(name, version)
            else:
                if prefix:
                    if prefix in data:
                        val = data[prefix][key]
                    else:
                        continue
                elif key in data:
                    val = data[key]
                else:
                    continue
            val, deferr = self.load_field(name, val, zf, version)
            if deferr:
                deferred.append((name, val, deferr))
            else:
                fields[name] = val
        obj = self.model(**fields)
        obj.clean()
        old_save = obj.save
        def _save(*args, **kwargs):
            del obj.save
            old_save(*args, **kwargs)
            for name, val, action in deferred:
                manager = getattr(obj, name)
                for item in val:
                    manager.add(item)
        obj.save = _save
        if commit:
            obj.save()
        return obj
        
    def get_field_docs(self, fieldname):
        try:
            field = self.model._meta.get_field(fieldname)
            if isinstance(field, models.ForeignKey):
                return _serializers[field.rel.to].docs()
            elif isinstance(field, models.ManyToManyField):
                spec = _serializers[field.rel.to].docs()
                spec['array'] = True
                return spec
            elif isinstance(field, models.ManyToOneRel):
                spec = _serializers[field.related_model].docs()
                spec['array'] = True
                return spec
            return FieldDocs(self.model, field)
        except models.FieldDoesNotExist:
            model = getattr(self.model, fieldname).related.related_model
            spec = _serializers[model].docs()
            spec['array'] = True
            return spec
        
    def docs(self):
        d = OrderedDict()
        for name in sorted(self.get_field_names()):
            prefix, key = self.split_prefix(name)
            info = self.get_field_docs(name)
            if prefix:
                d.setdefault(prefix, OrderedDict())
                d[prefix][key] = info
            else:
                d[name] = info
        return d


class DocumentTypeSerializer(object):
    def load(self, data, zf, version, commit=True):
        try:
            return DocumentType.objects.get(name=data)
        except DocumentType.DoesNotExist:
            raise ValueError("no such doctype: {1}".format(data))
            
    def docs(self):
        return FieldDocs(choices=[
            (doctype.name, doctype.name)
            for doctype in DocumentType.objects.all()
        ])
        
    def dump(self, obj, zf):
        return obj.name

class DocumentSerializer(ModelSerializer):
    def dump(self, obj, zf):
        assert obj.doctype.is_downloadable

        d = super().dump(obj, zf)

        zip_name = 'attachments/{}'.format(uuid4())
        if obj.mimetype == 'application/pdf':
            zip_name += '.pdf'
        f = obj.retrieve_raw()
        zf.writestr(zip_name, f.read())
        f.close()
        d['file'] = zip_name

        return d

    def load(self, data, zf, version, commit=True):
        obj = super().load(data, zf, version, commit=commit)
        if commit:
            with TemporaryFile() as f:
                f.write(zf.read(data['file']))
                f.flush()
                f.seek(0)
                obj.store(f)
        return obj


class EthicsCommissionSerializer(object):
    def load(self, data, zf, version, commit=False):
        try:
            return EthicsCommission.objects.get(uuid=data)
        except EthicsCommission.DoesNotExist:
            raise ValueError("no such ethicscommission: {}".format(data))
            
    def docs(self):
        return FieldDocs(choices=[
            (ec.uuid.hex, ec.name)
            for ec in EthicsCommission.objects.all()
        ])
        
    def dump(self, obj, zf):
        return obj.uuid.hex
        
class SubmissionSerializer(ModelSerializer):
    def __init__(self, **kwargs):
        super().__init__(Submission, **kwargs)
        
    def load(self, data, zf, version, commit=False):
        return Submission.objects.create(is_transient=True)
        

class SubmissionFormSerializer(ModelSerializer):
    def dump_field(self, fieldname, val, zf, obj):
        if fieldname == 'documents':
            val = val.filter(doctype__is_downloadable=True)
        return super().dump_field(fieldname, val, zf, obj)

    def load(self, data, zf, version, commit=True):
        obj = super().load(data, zf, version, commit=False)
        obj.is_transient = True
        if commit:
            obj.save()
        return obj

_serializers = {
    SubmissionForm: SubmissionFormSerializer(SubmissionForm,
        groups = (
            'study_plan', 'insurance', 'sponsor', 'invoice', 'german',
            'submitter', 'project_type', 'medtech', 'substance', 'subject',
        ),
        exclude = (
            'pdf_document', 'id', 'current_pending_vote',
            'current_published_vote', 'primary_investigator', 'submitter',
            'sponsor', 'presenter', 'is_transient', 'is_notification_update',
            'is_acknowledged',
        ),
        follow = (
            'participatingcenternonsubject_set',
            'foreignparticipatingcenter_set', 'investigators', 'measures',
            'documents', 'nontesteduseddrug_set',
        ),
    ),
    Submission: SubmissionSerializer(fields=('ec_number',)),
    Investigator: ModelSerializer(Investigator,
        exclude=('id', 'submission_form', 'user'),
        follow=('employees',)
    ),
    InvestigatorEmployee: ModelSerializer(InvestigatorEmployee,
        exclude=('id', 'investigator')
    ),
    Measure: ModelSerializer(Measure, exclude=('id', 'submission_form')),
    ParticipatingCenterNonSubject: ModelSerializer(
        ParticipatingCenterNonSubject,
        exclude=('id', 'submission_form')
    ),
    ForeignParticipatingCenter: ModelSerializer(ForeignParticipatingCenter,
        exclude=('id', 'submission_form')
    ),
    NonTestedUsedDrug: ModelSerializer(NonTestedUsedDrug,
        exclude=('id', 'submission_form')
    ),
    Document: DocumentSerializer(Document,
        fields=(
            'doctype', 'name', 'original_file_name', 'date', 'version',
            'mimetype',
        )
    ),
    DocumentType: DocumentTypeSerializer(),
    EthicsCommission: EthicsCommissionSerializer(),
}

def load_model_instance(model, data, zf, version, commit=True):
    if model not in _serializers:
        raise ValueError("cannot load objects of type {}".format(model))
    return _serializers[model].load(data, zf, version, commit=commit)

def dump_model_instance(obj, zf):
    if obj.__class__ not in _serializers:
        raise ValueError(
            "cannot serialize objecs of type {}".format(obj.__class__))
    return _serializers[obj.__class__].dump(obj, zf)
    
class _JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.astimezone(timezone.utc).strftime(DATETIME_FORMAT)
        elif isinstance(obj, datetime.date):
            return obj.strftime(DATE_FORMAT)
        return super().default(obj)

class Serializer(object):
    version = CURRENT_SERIALIZER_VERSION

    def read(self, file_like):
        zf = zipfile.ZipFile(file_like, 'r')
        data = json.loads(zf.read(DATA_JSON_NAME).decode('utf-8'))
        submission_form = _serializers[SubmissionForm].load(
            data['data'], zf, data['version'])
        return submission_form
    
    def write(self, submission_form, file_like):
        zf = zipfile.ZipFile(file_like, 'w', zipfile.ZIP_DEFLATED)
        
        data = {
            'version': self.version,
            'type': 'SubmissionForm',
            'data': dump_model_instance(submission_form, zf),
        }
        zf.writestr(DATA_JSON_NAME,
            json.dumps(data, cls=_JsonEncoder, indent=2, sort_keys=True).encode('utf-8'))
    
    def docs(self):
        return _serializers[SubmissionForm].docs()
            
