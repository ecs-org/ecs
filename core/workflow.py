from ecs import workflow
from ecs.core.models import Submission, SubmissionForm

@workflow.activity(model=Submission)
def change_submission_form(token):
    pass

# UC-11
@workflow.activity(model=Submission)
def inspect_form_and_content_completeness(token):
    pass

# UC-44
@workflow.activity(model=Submission)
def acknowledge_submission(token):
    pass

# UC-12
@workflow.activity(model=Submission)
def filter_retrospective_thesis(token):
    pass

# UC-12
@workflow.activity(model=Submission)
def review_retrospective_thesis(token):
    pass

# FIXME: does this really differ from 'review_retrospective_thesis' ?
# UC-12
@workflow.activity(model=Submission)
def rereview_retrospective_thesis(token):
    pass

# UC-12
@workflow.activity(model=Submission)
def assign_expedited_review_class(token):
    pass

# UC-12
@workflow.activity(model=Submission)
def assign_internal_review_class(token):
    pass

# UC-12
@workflow.activity(model=Submission)
def assign_internal_reviewer(token):
    pass

# UC-12 / UC-15 (reassign)
@workflow.activity(model=Submission)
def assign_external_reviewer(token):
    pass

# UC-16
@workflow.activity(model=Submission)
def review_external(token):
    pass

# UC-42 (placeholder)
@workflow.activity(model=Submission)
def review_legal_and_patient_data(token):
    pass
    
# UC-42 (placeholder)
@workflow.activity(model=Submission)
def review_statistical_issues(token):
    pass

# UC-41 (placeholder)
@workflow.activity(model=Submission)
def review_insurance_issues(token):
    pass

# UC-12
@workflow.activity(model=Submission)
def review_scientific_issues(token):
    pass

# UC-14
@workflow.activity(model=Submission)
def contact_external_reviewer(token):
    pass

@workflow.activity(model=Submission)
def do_external_review(token):
    pass


@workflow.control(model=Submission)
def reject(token):
    workflow.patterns.generic(token)

@workflow.control(model=Submission)
def accept(token):
    workflow.patterns.generic(token)
    
@workflow.guard(model=Submission)
def is_classified_for_external_review(workflow):
    return workflow.data.external_reviewer is True

@workflow.guard(model=Submission)
def is_accepted(workflow):
    return True

@workflow.guard(model=Submission)
def is_marked_as_thesis_by_submitter(workflow):
    return bool(workflow.data.get_most_recent_form().project_type_education_context)
    
@workflow.guard(model=Submission)
def is_thesis_and_retrospective(workflow):
    submission = workflow.data
    return submission.thesis and submission.retrospective

