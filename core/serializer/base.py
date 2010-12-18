import zipfile, os, uuid, datetime
from StringIO import StringIO

from django.utils import simplejson
from django.db import models
from django.core.files.base import File, ContentFile
from django.utils.datastructures import SortedDict
from django.contrib.contenttypes import generic

from ecs.core.models import SubmissionForm, Submission, EthicsCommission, Investigator, InvestigatorEmployee, Measure, ForeignParticipatingCenter, NonTestedUsedDrug
from ecs.documents.models import Document, DocumentType
from ecs.utils.countries.models import Country

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S+01:00'
DATE_FORMAT = '%Y-%m-%d'
DATA_JSON_NAME = 'data.json'

class FieldDocs(object):
    value = True

    def __init__(self, model=None, field=None, constraint=None, json_type=None, choices=None):
        self.model = model
        self.field = field
        self.constraint = constraint
        self._json_type = json_type
        self.choices = choices

    def json_type(self):
        if self._json_type:
            return self._json_type
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
        if self.constraint:
            c.append(self.constraint)
        if isinstance(self.field, models.DateTimeField):
            c.append("RFC 3339 with timezone UTC+1 (e.g. 2010-07-14T16:04:35+01:00)")
        elif isinstance(self.field, models.DateField):
            c.append("ISO 8601 with timezone UTC+1 (e.g. 2010-07-14)")
        elif isinstance(self.field, models.CharField):
            c.append("max. %s characters" % self.field.max_length)
        elif isinstance(self.field, models.FileField):
            c.append("valid internal zip file path")
        if self.field.null:
            c.append("may be null")
        return c
            
    def paperform_info(self):
        from ecs.core.paper_forms import get_field_info
        return get_field_info(self.model, self.field.name)


class ModelSerializer(object):
    exclude = ('id',)
    groups = ()
    follow = {}
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
            
    def get_field_names(self):
        names = set(f.name for f in self.model._meta.fields if f.name not in self.exclude)
        if self.fields:
            names = names.intersection(self.fields)
        return names.union(self.follow.keys())
        
    def get_reverse_name(self, follow_name):
        return self.follow.get(follow_name)
        
    def split_prefix(self, name):
        prefix, key = None, name
        for group in self.groups:
            if name.startswith(group):
                prefix, key = group, name[len(group)+1:]
                break
        return prefix, key
        
    def dump_field(self, fieldname, val, zf):
        if val is None or isinstance(val, (bool, basestring, int, long, datetime.datetime, datetime.date)):
            return val
        if hasattr(val, 'all') and hasattr(val, 'count'):
            try:
                return [dump_model_instance(x, zf) for x in val.all()]
            except ValueError, e:
                raise ValueError("cannot dump %s.%s: %s" % (self.model.__name__, fieldname, e))
        
        field = self.model._meta.get_field(fieldname)

        if isinstance(field, models.ForeignKey):
            return dump_model_instance(val, zf)
        elif isinstance(field, models.FileField):
            name, ext = os.path.splitext(val.name)
            zip_name = 'attachments/%s%s' % (uuid.uuid4(), ext)
            zf.write(val.path, zip_name)
            return zip_name
        else:
            raise ValueError("cannot serialize objects of type %s" % type(val))
        
        return val

    def dump(self, obj, zf):
        d = {}
        for name in self.get_field_names():
            prefix, key = self.split_prefix(name)
            data = self.dump_field(name, getattr(obj, name), zf)
            if prefix:
                d.setdefault(prefix, {})
                d[prefix][key] = data
            else:
                d[name] = data
        return d
        
    def load_many(self, model, val, zf, commit=True):
        return [load_model_instance(model, data, zf, commit=commit) for data in val]
        
    def load_field(self, fieldname, val, zf):
        if val is None:
            return val, False
        try:
            field = self.model._meta.get_field(fieldname)
        except models.fields.FieldDoesNotExist:
            field = None
        deferr = False
        if field:
            if isinstance(field, models.DateTimeField):
                val = datetime.datetime.strptime(val, DATETIME_FORMAT)
            elif isinstance(field, models.DateField):
                val = datetime.date.strptime(val, DATE_FORMAT)
            elif isinstance(field, models.ManyToManyField):
                val = self.load_many(field.related.parent_model, val, zf)
                deferr = True
            elif isinstance(field, models.FileField):
                f = ContentFile(zf.read(val))
                f.name = val # we hack in a name, to force django to automatically save the ContentFile on Model.save()
                val = f
            elif isinstance(field, models.ForeignKey):
                val = load_model_instance(field.rel.to, val, zf)
            elif isinstance(field, generic.GenericRelation):
                val = self.load_many(field.rel.to, val, zf, commit=False)
                deferr = True
        elif isinstance(val, list):
            rel_model = getattr(self.model, fieldname).related.model
            val = self.load_many(rel_model, val, zf, commit=False)
            deferr = True
        return val, deferr
        
    def load(self, data, zf, commit=True):
        deferred = []
        fields = {}
        obj = self.model()
        for name in self.get_field_names():
            prefix, key = self.split_prefix(name)
            if prefix:
                if prefix in data:
                    val = data[prefix][key]
                else:
                    continue
            elif key in data:
                val = data[key]
            else:
                continue
            val, deferr = self.load_field(name, val, zf)
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
                try:
                    return _serializers[field.rel.to].docs()
                except KeyError:
                    print fieldname, self.model
            if isinstance(field, models.ManyToManyField):
                spec = _serializers[field.rel.to].docs()
                spec['array'] = True
                return spec
            return FieldDocs(self.model, field)
        except models.FieldDoesNotExist:
            try:
                model = getattr(self.model, fieldname).related.model
                spec = _serializers[model].docs()
                spec['array'] = True
                return spec
            except AttributeError:
                raise
        
    def docs(self):
        d = SortedDict()
        for name in self.get_field_names():
            prefix, key = self.split_prefix(name)
            info = self.get_field_docs(name)
            if prefix:
                d.setdefault(prefix, {})
                d[prefix][key] = info
            else:
                d[name] = info
        d.keyOrder = list(sorted(d.keys()))
        return d


class DocumentTypeSerializer(object):
    def load(self, data, zf, commit=True):
        try:
            return DocumentType.objects.get(name=data)
        except DocumentType.DoesNotExist:
            raise ValueError("no such doctype: %s" % data)
            
    def docs(self):
        return FieldDocs(choices=[('"%s"' % doctype.name, doctype.name) for doctype in DocumentType.objects.all()])
        
    def dump(self, obj, zf):
        return obj.name

class EthicsCommissionSerializer(object):
    def load(self, data, zf, commit=False):
        try:
            return EthicsCommission.objects.get(uuid=data)
        except EthicsCommission.DoesNotExist:
            raise ValueError("no such ethicscommission: %s" % data)
            
    def docs(self):
        return FieldDocs(choices=[('"%s"' % ec.uuid, ec.name) for ec in EthicsCommission.objects.all()])
        
    def dump(self, obj, zf):
        return obj.uuid
        
class SubmissionSerializer(ModelSerializer):
    def __init__(self, **kwargs):
        super(SubmissionSerializer, self).__init__(Submission, **kwargs)
        
    def load(self, data, zf, commit=False):
        return Submission.objects.create()
        
class CountrySerializer(object):
    def dump(self, obj, zf):
        return obj.iso
        
    def load(self, data, zf, commit=False):
        return Country.objects.get(iso=data)

_serializers = {
    SubmissionForm: ModelSerializer(SubmissionForm,
        groups = ('study_plan', 'insurance', 'sponsor', 'invoice', 'german', 'submitter', 'project_type', 'medtech', 'substance', 'subject'),
        exclude = ('pdf_document', 'id', 'current_pending_vote', 'current_published_vote', 'primary_investigator', 'submitter', 'sponsor', 'presenter'),
        follow = {
            'foreignparticipatingcenter_set': 'submission_form',
            'investigators': 'submission_form',
            'measures': 'submission_form',
            'documents': '_submission_forms',
            'nontesteduseddrug_set': 'submission_form',
            'substance_registered_in_countries': 'submission_forms',
            'substance_p_c_t_countries': 'submissionform_set',
        },
    ),
    Submission: SubmissionSerializer(fields=('ec_number')),
    Investigator: ModelSerializer(Investigator, exclude=('id', 'submission_form', 'user'), follow={'employees': 'investigator'}),
    InvestigatorEmployee: ModelSerializer(InvestigatorEmployee, exclude=('id', 'investigator')),
    Measure: ModelSerializer(Measure, exclude=('id', 'submission_form')),
    ForeignParticipatingCenter: ModelSerializer(ForeignParticipatingCenter, exclude=('id', 'submission_form')),
    NonTestedUsedDrug: ModelSerializer(NonTestedUsedDrug, exclude=('id', 'submission_form')),
    Document: ModelSerializer(Document, fields=('doctype', 'file', 'original_file_name', 'date', 'version', 'mimetype')),
    DocumentType: DocumentTypeSerializer(),
    EthicsCommission: EthicsCommissionSerializer(),
    Country: CountrySerializer(),
}

def load_model_instance(model, data, zf, commit=True):
    if model not in _serializers:
        raise ValueError("cannot load objects of type %s" % model)
    return _serializers[model].load(data, zf, commit=commit)

def dump_model_instance(obj, zf):
    if obj.__class__ not in _serializers:
        raise ValueError("cannot serialize objecs of type %s" % obj.__class__)
    return _serializers[obj.__class__].dump(obj, zf)
    
class _JsonEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime(DATETIME_FORMAT)
        elif isinstance(obj, datetime.date):
            return obj.strftime(DATE_FORMAT)
        return super(Encoder, self).default(obj)

class Serializer(object):
    version = '0.1'

    def read(self, file_like):
        zf = zipfile.ZipFile(file_like, 'r')
        data = simplejson.loads(zf.read(DATA_JSON_NAME))
        submission_form = _serializers[SubmissionForm].load(data['data'], zf)
        return submission_form
    
    def write(self, submission_form, file_like):
        zf = zipfile.ZipFile(file_like, 'w', zipfile.ZIP_DEFLATED)
        
        data = {
            'version': self.version,
            'type': 'SubmissionForm',
            'data': dump_model_instance(submission_form, zf),
        }
        json = simplejson.dumps(data, cls=_JsonEncoder, indent=2)
        zf.writestr(DATA_JSON_NAME, json)
    
    def docs(self):
        return _serializers[SubmissionForm].docs()
            
