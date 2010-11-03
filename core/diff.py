# -*- coding: utf-8 -*-
import datetime
from django.utils.translation import ugettext as _
from django.db import models
from django.http import HttpRequest
from ecs.utils.diff_match_patch import diff_match_patch

from ecs.core.models import SubmissionForm, Investigator, EthicsCommission, \
    Measure, NonTestedUsedDrug, ForeignParticipatingCenter
from ecs.documents.models import Document, DocumentType
from ecs.core.forms import SubmissionFormForm
from ecs.utils.viewutils import render_html


DATETIME_FORMAT = '%d.%m.%Y %H:%M'
DATE_FORMAT = '%d.%m.%Y'

class Node(object):
    type = None
    def __init__(self, content):
        self.content = content

    def diff(self, other):
        raise NotImplementedError

    def __unicode__(self):
        return unicode(self.content)

class TextNode(Node):
    type = 'text'

    def diff(self, other):
        differ = diff_match_patch()

        diff = differ.diff_main(self.content, other.content)
        differ.diff_cleanupSemantic(diff)

        return diff

class AtomicTextNode(Node):
    type = 'atomic_text'

    def diff(self, other):
        if self.content == other.content:
            return [(0, self.content)]
        else:
            return [(-1, self.content), (1, other.content)]

class ListNode(Node):
    type = 'list'

    def diff(self, other):
        diff = []
        all_elements = set(self.content).union(other.content)

        for elem in all_elements:
            if not elem in self.content:   # new
                diff.append((1, unicode(elem)))
            elif not elem in other.content: # old
                diff.append((-1, unicode(elem)))
            else:
                diff.append((0, unicode(elem)))

        return diff

class ModelRenderer(object):
    exclude = ()
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
            return AtomicTextNode(_('No Information'))
        elif val is True:
            return AtomicTextNode(_('Yes'))
        elif val is False:
            return AtomicTextNode(_('No'))
        elif isinstance(val, datetime.date):
            return AtomicTextNode(val.strftime(DATE_FORMAT))
        elif isinstance(val, datetime.date):
            return AtomicTextNode(val.strftime(DATETIME_FORMAT))
        elif hasattr(val, 'all') and hasattr(val, 'count'):
            return ListNode([TextNode(render_model_instance(x, plain=True)) for x in val.all()])
        
        field = self.model._meta.get_field(name)

        if isinstance(field, models.ForeignKey):
            return TextNode(render_model_instance(val, plain=True))
        else:
            return TextNode(unicode(val))
        
    def render(self, instance, plain=False):
        d = {}

        for name in self.get_field_names():
            d[name] = self.render_field(instance, name)

        if plain:
            d = '<br />\n'.join([u'%s: %s' % (x[0], x[1]) for x in d.items()])
            d += '<br />\n'

        return d


class DocumentRenderer(ModelRenderer):
    def __init__(self, **kwargs):
        kwargs['model'] = Document
        return super(DocumentRenderer, self).__init__(**kwargs)

    def render(self, instance, plain=False):
        html = render_html(HttpRequest(), 'submissions/diff/document.inc', {'doc': instance})
        if plain:
            return html
        else:
            return {'link': html}
        

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
    Document: DocumentRenderer(),
    DocumentType: ModelRenderer(DocumentType, fields=('name',)),
    Measure: ModelRenderer(Measure, exclude=('id', 'submission_form')),
    NonTestedUsedDrug: ModelRenderer(NonTestedUsedDrug, exclude=('id', 'submission_form')),
    ForeignParticipatingCenter: ModelRenderer(ForeignParticipatingCenter, exclude=('id', 'submission_form')),
}

def render_model_instance(instance, plain=False):
    return _renderers[instance.__class__].render(instance, plain=plain)


def diff_submission_forms(old_submission_form, new_submission_form):
    assert(old_submission_form.submission == new_submission_form.submission)

    form = SubmissionFormForm(None, instance=old_submission_form)
    differ = diff_match_patch()

    old = render_model_instance(old_submission_form)
    new = render_model_instance(new_submission_form)

    diffs = []
    for field in sorted(old.keys()):
        diff = old[field].diff(new[field])
        if differ.diff_levenshtein(diff or []):
            try:
                label = form.fields[field].label
            except KeyError:
                label = field
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

