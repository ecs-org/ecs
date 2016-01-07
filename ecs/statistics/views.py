from django.shortcuts import render
from django.utils import timezone

from ecs.users.utils import user_flag_required
from ecs.core.models import SubmissionForm
from ecs.statistics.stats import collect_submission_stats_for_year


@user_flag_required('is_internal')
def stats(request, year=None):
    current_year = int(year) if year else timezone.now().year
    try:
        first_submission = SubmissionForm.objects.order_by('created_at')[0]
        first_year = first_submission.created_at.year
    except IndexError:
        first_year = current_year
    last_year = timezone.now().year

    return render(request, 'statistics/index.html', {
        'current_year': current_year,
        'years': range(first_year, last_year + 1),
        'stats': collect_submission_stats_for_year(current_year),
    })
