import datetime
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from ecs.core.models import Submission
from ecs.core.views.utils import render

from ecs.billing.models import Price


def submission_billing(request):
    unbilled_submissions = list(Submission.objects.filter(billed_at=None))
    for submission in unbilled_submissions:
        submission.price = Price.objects.get_for_submission(submission)

    if request.method == 'POST':
        selected_for_billing = []
        for submission in unbilled_submissions:
            if request.POST.get('bill_%s' % submission.pk, False):
                selected_for_billing.append(submission)
        
        Submission.objects.filter(pk__in=[s.pk for s in selected_for_billing]).update(billed_at=datetime.datetime.now())
        return HttpResponseRedirect(reverse('ecs.billing.views.submission_billing'))

    return render(request, 'billing/submissions.html', {
        'submissions': unbilled_submissions,
    })
    

def external_review_billing(request):
    return render(request, 'billing/external_review.html', {
    
    })