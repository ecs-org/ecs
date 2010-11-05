# -*- coding: utf-8 -*-
import datetime
from django.utils.translation import ugettext as _
from django.db import models
from django.http import HttpRequest
from django.contrib.contenttypes.models import ContentType
from ecs.utils.diff_match_patch import diff_match_patch

from ecs.core.models import SubmissionForm, Investigator, EthicsCommission, \
    Measure, NonTestedUsedDrug, ForeignParticipatingCenter
from ecs.documents.models import Document, DocumentType
from ecs.utils.viewutils import render_html
from ecs.audit.models import AuditTrail
from ecs.core import paper_forms


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
                status = 1
            elif not elem in other.content: # old
                status = -1
            else:
                status = 0

            html = u'<div class="elem">%s</div>' % elem
            diff.append((status, html))

        return diff

class ModelRenderer(object):
    exclude = ()
    fields = ()
    follow = ()

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
        return names.union(self.follow)

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
            return ListNode([render_model_instance(x, plain=True) for x in val.all()])
        
        field = self.model._meta.get_field(name)

        if isinstance(field, models.ForeignKey):
            return TextNode(render_model_instance(val, plain=True))
        else:
            return TextNode(unicode(val))
        
    def render(self, instance, plain=False):
        d = {}

        for name in self.get_field_names():
            d[name] = self.render_field(instance, name)

        if not plain:
            return d

        text = ''
        for field, value in d.items():
            field_info = paper_forms.get_field_info(instance.__class__, field, None)
            if field_info is not None:
                label = field_info.label
            else:
                label = field

            text += '%s: %s<br />\n' % (label, value)

        return text


class DocumentRenderer(ModelRenderer):
    def __init__(self, **kwargs):
        kwargs['model'] = Document
        return super(DocumentRenderer, self).__init__(**kwargs)

    def render(self, instance, plain=False):
        if not plain:
            raise NotImplementedError

        return render_html(HttpRequest(), 'submissions/diff/document.inc', {'doc': instance})

class ForeignParticipatingCenterRenderer(ModelRenderer):
    def __init__(self, **kwargs):
        kwargs['model'] = ForeignParticipatingCenter
        return super(ForeignParticipatingCenterRenderer, self).__init__(**kwargs)

    def render(self, instance, plain=False):
        if not plain:
            raise NotImplementedError

        return _(u'Name: %(name)s, Investigator: %(investigator)s') % {'name': instance.name, 'investigator': instance.investigator_name}


_renderers = {
    SubmissionForm: ModelRenderer(SubmissionForm,
        exclude=('id', 'submission', 'current_for', 'primary_investigator', 'current_for_submission', 'pdf_document'),
        follow=('foreignparticipatingcenter_set','investigators','measures','nontesteduseddrug_set','documents'),
    ),
    Investigator: ModelRenderer(Investigator,
        exclude=('id', 'submission_form',),
    ),
    EthicsCommission: ModelRenderer(EthicsCommission, exclude=('uuid',)),
    Measure: ModelRenderer(Measure, exclude=('id', 'submission_form')),
    NonTestedUsedDrug: ModelRenderer(NonTestedUsedDrug, exclude=('id', 'submission_form')),
    ForeignParticipatingCenter: ForeignParticipatingCenterRenderer(),
    Document: DocumentRenderer(),
}

def render_model_instance(instance, plain=False):
    return _renderers[instance.__class__].render(instance, plain=plain)


def diff_submission_forms(old_submission_form, new_submission_form):
    assert(old_submission_form.submission == new_submission_form.submission)
    submission = new_submission_form.submission

    differ = diff_match_patch()

    old = render_model_instance(old_submission_form)
    new = render_model_instance(new_submission_form)

    diffs = []
    for field in sorted(old.keys()):
        diff = old[field].diff(new[field])
        if differ.diff_levenshtein(diff or []):
            field_info = paper_forms.get_field_info(SubmissionForm, field, None)
            if field_info is not None:
                label = field_info.label
            else:
                label = field

            diffs.append((label, diff))
    
    return diffs

