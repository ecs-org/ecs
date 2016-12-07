import time

from celery.task import task

from django.db import transaction

from ecs.core.models import SubmissionForm


@task()
@transaction.atomic
def render_submission_form(submission_form_id=None):
    logger = render_submission_form.get_logger()

    # XXX: Look to wait for submission form to appear. The celery task is
    # triggered on submit before the request transaction is committed, so we
    # have to wait. We should start using transaction.on_commit() as soon as
    # we've updated to Django 1.9.
    sf = None
    for i in range(60):
        try:
            sf = SubmissionForm.unfiltered.select_for_update().get(id=submission_form_id)
            break
        except SubmissionForm.DoesNotExist:
            time.sleep(1)
    if not sf:
        logger.error("SubmissionForm(id=%d) didn't appear", submission_form_id)

    sf.render_pdf_document()
