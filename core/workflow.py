from ecs import workflow
from ecs.core.models import Submission, SubmissionForm

# UC-11
@workflow.activity(model=SubmissionForm)
def inspect_form_and_content_completeness(token):
    pass

# UC-44
@workflow.activity(model=SubmissionForm)
def acknowledge_submission(token):
    pass

# UC-12
@workflow.activity(model=SubmissionForm)
def filter_retrospective_thesis(token):
    pass

# UC-12
@workflow.activity(model=SubmissionForm)
def review_retrospective_thesis(token):
    pass

# FIXME: does this really differ from 'review_retrospective_thesis' ?
# UC-12
@workflow.activity(model=SubmissionForm)
def rereview_retrospective_thesis(token):
    pass

# UC-12
@workflow.activity(model=SubmissionForm)
def assign_expedited_review_class(token):
    pass

# UC-12
@workflow.activity(model=SubmissionForm)
def assign_internal_review_class(token):
    pass

# UC-12
@workflow.activity(model=SubmissionForm)
def assign_internal_reviewer(token):
    pass

# UC-12 / UC-15 (reassign)
@workflow.activity(model=SubmissionForm)
def assign_external_reviewer(token):
    pass

# UC-16
@workflow.activity(model=SubmissionForm)
def review_external(token):
    pass

@workflow.guard(model=SubmissionForm)
def is_marked_as_thesis_by_submitter(workflow):
    return bool(workflow.data.project_type_education_context)
    
@workflow.guard(model=SubmissionForm)
def is_thesis_and_retrospective(workflow):
    submission = workflow.data.submission
    return submission.thesis and submission.retrospective

