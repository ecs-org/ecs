from django.shortcuts import get_object_or_404, redirect, render

from ecs.users.utils import user_flag_required
from ecs.core.models import Submission, Comment
from ecs.core.forms import CommentForm


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

    form = CommentForm(request.POST or None, instance=comment)
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.submission = submission
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
