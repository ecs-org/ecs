# -*- coding: utf-8 -*-
import datetime
from django.utils.translation import ugettext as _
from ecs.utils.diff_match_patch import diff_match_patch

from ecs.core.models import SubmissionForm


DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S+01:00'
DATE_FORMAT = '%Y-%m-%d'


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
        value = getattr(instance, name)
        if value is None:
            return _('No Information')
        elif value is True:
            return _('Yes')
        elif value is False:
            return _('No')
        elif isinstance(value, datetime.date):
            return value.strftime(DATE_FORMAT)
        elif isinstance(value, datetime.date):
            return value.strftime(DATETIME_FORMAT)
        else:
            return unicode(value)

    def render(self, instance):
        d = {}

        for name in self.get_field_names():
            d[name] = self.render_field(instance, name)

        return d


_renderers = {
    SubmissionForm: ModelRenderer(SubmissionForm,
        exclude=('submission', 'current_for', 'primary_investigator', 'current_for_submission', 'documents'),
        follow = {
            'foreignparticipatingcenter_set': 'submission_form',
            'investigators': 'submission_form',
            'measures': 'submission_form',
            'documents': 'parent_object',
            'nontesteduseddrug_set': 'submission_form',
        },
    ),
}


def diff(request, old_submission_form_pk, new_submission_form_pk):
    old_submission_form = get_object_or_404(SubmissionForm, pk=old_submission_form_pk)
    new_submission_form = get_object_or_404(SubmissionForm, pk=new_submission_form_pk)

    sff = SubmissionFormForm(None, instance=old_submission_form)

    differ = diff_match_patch()
    diffs = []

    old = _render_submission_form(old_submission_form, ignored_fields=ignored_fields)
    new = _render_submission_form(new_submission_form, ignored_fields=ignored_fields)

    for field in sorted(old.keys()):
        diff = differ.diff_main(old[field], new[field])
        if differ.diff_levenshtein(diff):
            try:
                label = sff.fields[field].label
            except KeyError:
                label = field
            differ.diff_cleanupSemantic(diff)
            diffs.append((label, diff))

    
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

