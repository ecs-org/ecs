from ecs.core.views.utils import render, redirect_to_next_url, CsrfExemptBaseHandler
from ecs.core.views.core import demo, index
from ecs.core.views.core import download_document
from ecs.core.views.core import notification_list, view_notification, submission_data_for_notification, select_notification_creation_type, create_notification, notification_pdf
from ecs.core.views.core import create_submission_form, copy_submission_form, view_submission_form, submission_pdf, submission_form_list
from ecs.core.views.meetings import meeting_list, create_meeting, timetable_editor, add_timetable_entry, remove_timetable_entry, update_timetable_entry, \
    move_timetable_entry, optimize_timetable, participation_editor, users_by_medical_category