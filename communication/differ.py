# -*- coding: utf-8 -*-
from ecs.utils.diff_match_patch import diff_match_patch


class SubmissionFormDiff(list):

def _render_submission_form(instance, ignored_fields=[]):
    ignored_fields = list(ignored_fields)

    fields = [x for x in instance.__class__._meta.get_all_field_names() if not x in list(ignored_fields)+['id']]
    fields.sort()

    rendered_fields = {}
    for field in fields:
        try:
            value = getattr(instance, field) or ''
        except AttributeError:
            try:
                value = getattr(instance, '%s_set' % field) or ''
            except AttributeError, e:
                print 'Error: %s %s: %s' % (instance, field, e)
                continue
        except Exception, e:
            print 'Error: %s %s: %s' % (instance, field, e)
            continue

        if hasattr(value, 'all'):  # x-to-many-relation
            rendered = u', '.join([unicode(x) for x in value.all()])
        elif isinstance(value, models.Model):  # foreign-key
            rendered = unicode(value)
        else:  # all other values
            rendered = unicode(value).replace(u'\n', u'<br />\n')


        rendered_fields[field] = rendered

    return rendered_fields

def diff(request, old_submission_form_pk, new_submission_form_pk):
    old_submission_form = get_object_or_404(SubmissionForm, pk=old_submission_form_pk)
    new_submission_form = get_object_or_404(SubmissionForm, pk=new_submission_form_pk)

    sff = SubmissionFormForm(None, instance=old_submission_form)

    differ = diff_match_patch()
    diffs = []

    ignored_fields = ('submission', 'current_for', 'primary_investigator', 'current_for_submission', 'documents')
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

