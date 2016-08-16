import mimetypes

from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ecs.users.utils import user_flag_required
from ecs.core.models import Submission, Comment
from ecs.core.forms import CommentForm
from ecs.documents.models import Document, DocumentType
from ecs.documents.views import handle_download


@user_flag_required('is_internal')
def index(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    comments = submission.comment_set.order_by('id')
    return render(request, 'comments/index.html', {
        'submission': submission,
        'comments': comments,
    })


@user_flag_required('is_internal')
def edit(request, submission_pk=None, pk=None):
    assert submission_pk or pk
    if pk:
        comment = get_object_or_404(Comment, pk=pk)
        submission = comment.submission
    else:
        comment = None
        submission = get_object_or_404(Submission, pk=submission_pk)

    form = CommentForm(request.POST or None, request.FILES or None,
        instance=comment)
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.submission = submission
        comment.save()

        f = form.cleaned_data.get('file')
        if f:
            doctype = DocumentType.objects.get(identifier='other')
            mimetype = mimetypes.guess_type(f.name)[0]
            attachment = Document.objects.create(original_file_name=f.name,
                mimetype=(mimetype or 'application/octet-stream'),
                stamp_on_download=False, name=f.name, doctype=doctype,
                version='', date=timezone.now(), parent_object=comment)
            attachment.store(f)

            comment.attachment = attachment
            comment.save()

        return redirect('ecs.core.views.comments.index',
            submission_pk=comment.submission.pk)
    return render(request, 'comments/form.html', {'form': form})


@user_flag_required('is_internal')
def delete(request, pk=None):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('ecs.core.views.comments.index',
        submission_pk=comment.submission.pk)


@user_flag_required('is_internal')
def download_attachment(request, pk=None, view=False):
    comment = get_object_or_404(Comment, pk=pk, attachment__isnull=False)
    return handle_download(request, comment.attachment, view=view)


def view_attachment(request, pk=None):
    return download_attachment(request, pk, view=True)
