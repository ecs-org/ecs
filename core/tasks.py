# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from celery.decorators import periodic_task

from ecs.core.models import Submission

@periodic_task(run_every=timedelta(seconds=10))
def finish_studies_with_expired_votes():
    for submission in Submission.objects.filter(is_finished=False).with_vote(positive=True, permanent=True, published=True, valid_until__lte=datetime.now()):
        submission.finish(expired=True)
