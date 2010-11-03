# -*- coding: utf-8 -*-
import datetime
from django.utils.translation import ugettext as _
from django.db import models
from ecs.utils.diff_match_patch import diff_match_patch

from ecs.core.models import SubmissionForm, Investigator, EthicsCommission, \
    Measure, NonTestedUsedDrug, ForeignParticipatingCenter
from ecs.documents.models import Document, DocumentType
from ecs.core.forms import SubmissionFormForm


DATETIME_FORMAT = '%d.%m.%Y %H:%M'
DATE_FORMAT = '%d.%m.%Y'


class ModelRenderer(object):
    exclude = ('id')
    fields = ()
    follow = {}

    def __init__(self, model, exclude=None, fields=None, follow=None):
        self.model = model
        if exclude:
            self.exclude = exclude
        if fields:
            self.fields = fields
        if follow:
            self.follow = follow

    def get_field_names(self):
        names = set(f.name for f in self.model._meta.fields if f.name not in self.exclude)
        if self.fields:
            names = names.intersection(self.fields)
        return names.union(self.follow.keys())

    def render_field(self, instance, name):
        val = getattr(instance, name)
        if val is None:
            return _('No Information')
        elif val is True:
            return _('Yes')
        elif val is False:
            return _('No')
        elif isinstance(val, datetime.date):
            return val.strftime(DATE_FORMAT)
        elif isinstance(val, datetime.date):
            return val.strftime(DATETIME_FORMAT)
        elif hasattr(val, 'all') and hasattr(val, 'count'):
            return [render_model_instance(x) for x in val.all()]
        
        field = self.model._meta.get_field(name)

        if isinstance(field, models.ForeignKey):
            return render_model_instance(val)
        else:
            return unicode(val)
        
    def render(self, instance):
        d = {}

        for name in self.get_field_names():
            d[name] = self.render_field(instance, name)

        return d


_renderers = {
    SubmissionForm: ModelRenderer(SubmissionForm,
        exclude=('id', 'submission', 'current_for', 'primary_investigator', 'current_for_submission', 'documents'),
        follow = {
            'foreignparticipatingcenter_set': 'submission_form',
            'investigators': 'submission_form',
            'measures': 'submission_form',
            'documents': 'parent_object',
            'nontesteduseddrug_set': 'submission_form',
        },
    ),
    Investigator: ModelRenderer(Investigator,
        exclude=('id', 'submission_form',),
    ),
    EthicsCommission: ModelRenderer(EthicsCommission, exclude=('uuid',)),
    Document: ModelRenderer(Document, fields=('doctype', 'file', 'date', 'version', 'mimetype')),
    DocumentType: ModelRenderer(DocumentType, fields=('name',)),
    Measure: ModelRenderer(Measure, exclude=('id', 'submission_form')),
    NonTestedUsedDrug: ModelRenderer(NonTestedUsedDrug, exclude=('id', 'submission_form')),
    ForeignParticipatingCenter: ModelRenderer(ForeignParticipatingCenter, exclude=('id', 'submission_form')),
}

def render_model_instance(instance):
    return _renderers[instance.__class__].render(instance)


def diff_submission_forms(old_submission_form, new_submission_form):
    assert(old_submission_form.submission == new_submission_form.submission)

    form = SubmissionFormForm(None, instance=old_submission_form)
    differ = diff_match_patch()

    old = render_model_instance(old_submission_form)
    new = render_model_instance(new_submission_form)

    diffs = []
    for field in sorted(old.keys()):
        diff = differ.diff_main(unicode(old[field]), unicode(new[field]))
        if differ.diff_levenshtein(diff):
            try:
                label = form.fields[field].label
            except KeyError:
                label = field
            differ.diff_cleanupSemantic(diff)
            diffs.append((label, diff))
    
    return diffs


def rofl():
    ctype = ContentType.objects.get_for_model(old_submission_form)
    old_document_creation_date = AuditTrail.objects.get(content_type__pk=ctype.id, object_id=old_submission_form.id, object_created=True).created_at
    new_document_creation_date = AuditTrail.objects.get(content_type__pk=ctype.id, object_id=new_submission_form.id, object_created=True).created_at

    ctype = ContentType.objects.get_for_model(Document)
    new_document_pks = [x.object_id for x in AuditTrail.objects.filter(content_type__pk=ctype.id, created_at__gt=old_document_creation_date, created_at__lte=new_document_creation_date)]

    ctype = ContentType.objects.get_for_model(old_submission_form)
    submission_forms = [x.pk for x in new_submission_form.submission.forms.all()]
    new_documents = Document.objects.filter(content_type__pk=ctype.id, object_id__in=submission_forms, pk__in=new_document_pks)

    print new_documents

    return render(request, 'submissions/diff.html', {
        'submission': new_submission_form.submission,
        'diffs': diffs,
        'new_documents': new_documents,
    })

