from ecs.core.views.submissions import (create_submission_form, copy_submission_form,
    readonly_submission_form, categorization_review, checklist_review, copy_latest_submission_form,
    vote_review, export_submission, import_submission_form, befangene_review, diff, submission_widget,
    submission_list, upload_document_for_submission, delete_document_from_submission,
    delete_docstash_entry, view_submission, all_submissions, my_submissions, assigned_submissions,
    delete_task, show_checklist_review, drop_checklist_review, change_submission_presenter,
    change_submission_susar_presenter, paper_submission_review, initial_review, vote_preparation,
    grant_temporary_access, revoke_temporary_access, b2_vote_preparation,
)
from ecs.core.views.autocomplete import autocomplete, internal_autocomplete
from ecs.core.views.fieldhistory import field_history
from ecs.core.views.administration import advanced_settings

# remove the following lines for the final product
from ecs.core.views.developer import (developer_test_pdf, test_pdf_html, test_render_pdf,
    developer_test_checklist_pdf, test_checklist_pdf_html, test_render_checklist_pdf,
    developer_test_notification_pdf, test_notification_pdf_html, test_render_notification_pdf,
    developer_test_notification_answer_pdf, test_notification_answer_pdf_html, test_render_notification_answer_pdf,
    developer_test_vote_pdf, test_vote_pdf_html, test_render_vote_pdf,
    developer_translations,
)
