from django.db import models, migrations


def rename_indices(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("select to_regclass('auth_group_permissions_group_id_key')")
        if cursor.fetchone()[0]:
            # rename all constraints and indices to modern names;
            # generated with apgdiff
            cursor.execute('''
                ALTER TABLE auth_group_permissions
                    DROP CONSTRAINT auth_group_permissions_group_id_key;

                ALTER TABLE auth_group_permissions
                    DROP CONSTRAINT auth_group_permissions_permission_id_fkey;

                ALTER TABLE auth_group_permissions
                    DROP CONSTRAINT group_id_refs_id_3cea63fe;

                ALTER TABLE auth_permission
                    DROP CONSTRAINT auth_permission_content_type_id_key;

                ALTER TABLE auth_permission
                    DROP CONSTRAINT content_type_id_refs_id_728de91f;

                ALTER TABLE auth_user_groups
                    DROP CONSTRAINT auth_user_groups_user_id_key;

                ALTER TABLE auth_user_groups
                    DROP CONSTRAINT auth_user_groups_group_id_fkey;

                ALTER TABLE auth_user_groups
                    DROP CONSTRAINT user_id_refs_id_7ceef80f;

                ALTER TABLE auth_user_user_permissions
                    DROP CONSTRAINT auth_user_user_permissions_user_id_key;

                ALTER TABLE auth_user_user_permissions
                    DROP CONSTRAINT auth_user_user_permissions_permission_id_fkey;

                ALTER TABLE auth_user_user_permissions
                    DROP CONSTRAINT user_id_refs_id_dfbab7d;

                ALTER TABLE billing_checklistbillingstate
                    DROP CONSTRAINT checklist_id_refs_id_43f0c068;

                ALTER TABLE billing_checklistpayment
                    DROP CONSTRAINT document_id_refs_id_1ce70d0d;

                ALTER TABLE billing_checklistpayment_checklists
                    DROP CONSTRAINT billing_checklistpayment_chec_checklistpayment_id_18198678_uniq;

                ALTER TABLE billing_checklistpayment_checklists
                    DROP CONSTRAINT checklist_id_refs_id_7b757308;

                ALTER TABLE billing_checklistpayment_checklists
                    DROP CONSTRAINT checklistpayment_id_refs_id_78302370;

                ALTER TABLE billing_invoice
                    DROP CONSTRAINT document_id_refs_id_468ba37;

                ALTER TABLE billing_invoice_submissions
                    DROP CONSTRAINT billing_invoice_submissions_invoice_id_34624016_uniq;

                ALTER TABLE billing_invoice_submissions
                    DROP CONSTRAINT invoice_id_refs_id_4dc69af7;

                ALTER TABLE billing_invoice_submissions
                    DROP CONSTRAINT submission_id_refs_id_7e851942;

                ALTER TABLE boilerplate_text
                    DROP CONSTRAINT boilerplate_text_slug_uniq;

                ALTER TABLE boilerplate_text
                    DROP CONSTRAINT author_id_refs_id_3a5dbb31;

                ALTER TABLE checklists_checklist
                    DROP CONSTRAINT checklists_checklist_blueprint_id_7708483f_uniq;

                ALTER TABLE checklists_checklist
                    DROP CONSTRAINT core_checklist_pdf_document_id_key;

                ALTER TABLE checklists_checklist
                    DROP CONSTRAINT blueprint_id_refs_id_4dcc0527;

                ALTER TABLE checklists_checklist
                    DROP CONSTRAINT last_edited_by_id_refs_id_950e58a;

                ALTER TABLE checklists_checklist
                    DROP CONSTRAINT pdf_document_id_refs_id_23c29a95;

                ALTER TABLE checklists_checklist
                    DROP CONSTRAINT submission_id_refs_id_1ad96dc8;

                ALTER TABLE checklists_checklist
                    DROP CONSTRAINT user_id_refs_id_84433da;

                ALTER TABLE checklists_checklistanswer
                    DROP CONSTRAINT checklist_id_refs_id_1ccec173;

                ALTER TABLE checklists_checklistanswer
                    DROP CONSTRAINT question_id_refs_id_73c118cf;

                ALTER TABLE checklists_checklistblueprint
                    DROP CONSTRAINT core_checklistblueprint_slug_key;

                ALTER TABLE checklists_checklistquestion
                    DROP CONSTRAINT checklists_checklistquestion_blueprint_id_106a54a6_uniq;

                ALTER TABLE checklists_checklistquestion
                    DROP CONSTRAINT core_checklistquestion_blueprint_id_41d1534e_uniq;

                ALTER TABLE checklists_checklistquestion
                    DROP CONSTRAINT blueprint_id_refs_id_76df151b;

                ALTER TABLE communication_message
                    DROP CONSTRAINT receiver_id_refs_id_7c29fc3f;

                ALTER TABLE communication_message
                    DROP CONSTRAINT reply_receiver_id_refs_id_7c29fc3f;

                ALTER TABLE communication_message
                    DROP CONSTRAINT reply_to_id_refs_id_2a6e57b;

                ALTER TABLE communication_message
                    DROP CONSTRAINT sender_id_refs_id_7c29fc3f;

                ALTER TABLE communication_message
                    DROP CONSTRAINT thread_id_refs_id_695bac9;

                ALTER TABLE communication_thread
                    DROP CONSTRAINT last_message_id_refs_id_72927337;

                ALTER TABLE communication_thread
                    DROP CONSTRAINT receiver_id_refs_id_7c2737fb;

                ALTER TABLE communication_thread
                    DROP CONSTRAINT related_thread_id_refs_id_2263bc85;

                ALTER TABLE communication_thread
                    DROP CONSTRAINT sender_id_refs_id_7c2737fb;

                ALTER TABLE communication_thread
                    DROP CONSTRAINT submission_id_refs_id_156e1a63;

                ALTER TABLE communication_thread
                    DROP CONSTRAINT task_id_refs_id_4f42f960;

                ALTER TABLE core_advancedsettings
                    DROP CONSTRAINT default_contact_id_refs_id_448ce2e0;

                ALTER TABLE core_expeditedreviewcategory
                    DROP CONSTRAINT core_expeditedreviewcategory_abbrev_uniq;

                ALTER TABLE core_expeditedreviewcategory_users
                    DROP CONSTRAINT core_expeditedreviewca_expeditedreviewcategory_id_53cb92cf_uniq;

                ALTER TABLE core_expeditedreviewcategory_users
                    DROP CONSTRAINT expeditedreviewcategory_id_refs_id_50926e7c;

                ALTER TABLE core_expeditedreviewcategory_users
                    DROP CONSTRAINT user_id_refs_id_6ea6d0ef;

                ALTER TABLE core_foreignparticipatingcenter
                    DROP CONSTRAINT submission_form_id_refs_id_49f71107;

                ALTER TABLE core_investigator
                    DROP CONSTRAINT ethics_commission_id_refs_id_6bf602e7;

                ALTER TABLE core_investigator
                    DROP CONSTRAINT submission_form_id_refs_id_4cd369ae;

                ALTER TABLE core_investigator
                    DROP CONSTRAINT user_id_refs_id_64b95f0e;

                ALTER TABLE core_investigatoremployee
                    DROP CONSTRAINT investigator_id_refs_id_29c3ab65;

                ALTER TABLE core_measure
                    DROP CONSTRAINT submission_form_id_refs_id_2cc2f9a0;

                ALTER TABLE core_medicalcategory_users
                    DROP CONSTRAINT core_medicalcategory_users_medicalcategory_id_33474797_uniq;

                ALTER TABLE core_medicalcategory_users
                    DROP CONSTRAINT medicalcategory_id_refs_id_6d3b670a;

                ALTER TABLE core_medicalcategory_users
                    DROP CONSTRAINT user_id_refs_id_23025dae;

                ALTER TABLE core_submission
                    DROP CONSTRAINT current_submission_form_id_refs_id_19098161;

                ALTER TABLE core_submission
                    DROP CONSTRAINT presenter_id_refs_id_6a58294d;

                ALTER TABLE core_submission
                    DROP CONSTRAINT susar_presenter_id_refs_id_6a58294d;

                ALTER TABLE core_submissionform
                    DROP CONSTRAINT current_pending_vote_id_refs_id_243b1915;

                ALTER TABLE core_submissionform
                    DROP CONSTRAINT current_published_vote_id_refs_id_243b1915;

                ALTER TABLE core_submissionform
                    DROP CONSTRAINT pdf_document_id_refs_id_17c85d4a;

                ALTER TABLE core_submissionform
                    DROP CONSTRAINT presenter_id_refs_id_27e12cbf;

                ALTER TABLE core_submissionform
                    DROP CONSTRAINT primary_investigator_id_refs_id_188468cc;

                ALTER TABLE core_submissionform
                    DROP CONSTRAINT sponsor_id_refs_id_27e12cbf;

                ALTER TABLE core_submissionform
                    DROP CONSTRAINT submission_id_refs_id_878d89f;

                ALTER TABLE core_submissionform
                    DROP CONSTRAINT submitter_id_refs_id_27e12cbf;

                ALTER TABLE core_nontesteduseddrug
                    DROP CONSTRAINT submission_form_id_refs_id_68925b25;

                ALTER TABLE core_submission_befangene
                    DROP CONSTRAINT core_submission_befangene_submission_id_70bc0268_uniq;

                ALTER TABLE core_submission_befangene
                    DROP CONSTRAINT submission_id_refs_id_22bb2537;

                ALTER TABLE core_submission_befangene
                    DROP CONSTRAINT user_id_refs_id_14340cf7;

                ALTER TABLE core_submission_expedited_review_categories
                    DROP CONSTRAINT core_submission_expedited_review_ca_submission_id_105c1db5_uniq;

                ALTER TABLE core_submission_expedited_review_categories
                    DROP CONSTRAINT expeditedreviewcategory_id_refs_id_df8255f;

                ALTER TABLE core_submission_expedited_review_categories
                    DROP CONSTRAINT submission_id_refs_id_3dc4cd2c;

                ALTER TABLE core_submission_external_reviewers
                    DROP CONSTRAINT core_submission_external_reviewers_submission_id_28dade8c_uniq;

                ALTER TABLE core_submission_external_reviewers
                    DROP CONSTRAINT submission_id_refs_id_35cd5;

                ALTER TABLE core_submission_external_reviewers
                    DROP CONSTRAINT user_id_refs_id_767b1c33;

                ALTER TABLE core_submission_medical_categories
                    DROP CONSTRAINT core_submission_medical_categories_submission_id_4c88601f_uniq;

                ALTER TABLE core_submission_medical_categories
                    DROP CONSTRAINT medicalcategory_id_refs_id_9dad7f3;

                ALTER TABLE core_submission_medical_categories
                    DROP CONSTRAINT submission_id_refs_id_4ce02ad1;

                ALTER TABLE core_submissionform_documents
                    DROP CONSTRAINT core_submissionform_documents_submissionform_id_25f995ff_uniq;

                ALTER TABLE core_submissionform_documents
                    DROP CONSTRAINT document_id_refs_id_3b1bae39;

                ALTER TABLE core_submissionform_documents
                    DROP CONSTRAINT submissionform_id_refs_id_501eb330;

                ALTER TABLE core_submissionform_substance_p_c_t_countries
                    DROP CONSTRAINT core_submissionform_substance_p_submissionform_id_3d589096_uniq;

                ALTER TABLE core_submissionform_substance_p_c_t_countries
                    DROP CONSTRAINT country_id_refs_iso_13f0cc1b;

                ALTER TABLE core_submissionform_substance_p_c_t_countries
                    DROP CONSTRAINT submissionform_id_refs_id_76df211;

                ALTER TABLE core_temporaryauthorization
                    DROP CONSTRAINT submission_id_refs_id_14ebe8cd;

                ALTER TABLE core_temporaryauthorization
                    DROP CONSTRAINT user_id_refs_id_655261d5;

                ALTER TABLE django_admin_log
                    DROP CONSTRAINT django_admin_log_content_type_id_fkey;

                ALTER TABLE django_admin_log
                    DROP CONSTRAINT django_admin_log_user_id_fkey;

                ALTER TABLE django_content_type
                    DROP CONSTRAINT django_content_type_app_label_key;

                ALTER TABLE docstash_docstash
                    DROP CONSTRAINT docstash_docstash_owner_id_2a5c319e_uniq;

                ALTER TABLE docstash_docstash
                    DROP CONSTRAINT content_type_id_refs_id_573a7868;

                ALTER TABLE docstash_docstash
                    DROP CONSTRAINT owner_id_refs_id_4771f41c;

                ALTER TABLE docstash_docstashdata
                    DROP CONSTRAINT docstash_docstashdata_version_1976c894_uniq;

                ALTER TABLE docstash_docstashdata
                    DROP CONSTRAINT stash_id_refs_key_6b6c54ef;

                ALTER TABLE documents_document
                    DROP CONSTRAINT documents_document_uuid_document_key;

                ALTER TABLE documents_document
                    DROP CONSTRAINT content_type_id_refs_id_7ca3cac4;

                ALTER TABLE documents_document
                    DROP CONSTRAINT doctype_id_refs_id_515fbef9;

                ALTER TABLE documents_document
                    DROP CONSTRAINT replaces_document_id_refs_id_22b81343;

                ALTER TABLE documents_downloadhistory
                    DROP CONSTRAINT document_id_refs_id_1d6e6519;

                ALTER TABLE documents_downloadhistory
                    DROP CONSTRAINT user_id_refs_id_21cd64de;

                ALTER TABLE meetings_assignedmedicalcategory
                    DROP CONSTRAINT meetings_assignedmedicalcategory_category_id_46bf0a6c_uniq;

                ALTER TABLE meetings_assignedmedicalcategory
                    DROP CONSTRAINT board_member_id_refs_id_5cfc455a;

                ALTER TABLE meetings_assignedmedicalcategory
                    DROP CONSTRAINT category_id_refs_id_40a585be;

                ALTER TABLE meetings_assignedmedicalcategory
                    DROP CONSTRAINT meeting_id_refs_id_1fe07247;

                ALTER TABLE meetings_constraint
                    DROP CONSTRAINT meeting_id_refs_id_5bf1d7d4;

                ALTER TABLE meetings_constraint
                    DROP CONSTRAINT user_id_refs_id_7c369735;

                ALTER TABLE meetings_participation
                    DROP CONSTRAINT entry_id_refs_id_1928ff4a;

                ALTER TABLE meetings_participation
                    DROP CONSTRAINT medical_category_id_refs_id_27fd6786;

                ALTER TABLE meetings_participation
                    DROP CONSTRAINT user_id_refs_id_31b72c3e;

                ALTER TABLE meetings_timetableentry
                    DROP CONSTRAINT meetings_timetableentry_meeting_id_8a249f5_uniq;

                ALTER TABLE meetings_timetableentry
                    DROP CONSTRAINT meeting_id_refs_id_16207286;

                ALTER TABLE meetings_timetableentry
                    DROP CONSTRAINT submission_id_refs_id_1c716539;

                ALTER TABLE notifications_amendmentnotification
                    DROP CONSTRAINT new_submission_form_id_refs_id_35fe166a;

                ALTER TABLE notifications_amendmentnotification
                    DROP CONSTRAINT notification_ptr_id_refs_id_3e1960c9;

                ALTER TABLE notifications_amendmentnotification
                    DROP CONSTRAINT old_submission_form_id_refs_id_35fe166a;

                ALTER TABLE notifications_completionreportnotification
                    DROP CONSTRAINT notifications_completionreportnotificat_notification_ptr_id_key;

                ALTER TABLE notifications_completionreportnotification
                    DROP CONSTRAINT notification_ptr_id_refs_id_5a45d1d1;

                ALTER TABLE notifications_notification
                    DROP CONSTRAINT pdf_document_id_refs_id_5697be71;

                ALTER TABLE notifications_notification
                    DROP CONSTRAINT type_id_refs_id_7e236c5f;

                ALTER TABLE notifications_notification
                    DROP CONSTRAINT user_id_refs_id_5c79cb54;

                ALTER TABLE notifications_notification_documents
                    DROP CONSTRAINT notifications_notification_docume_notification_id_485d0527_uniq;

                ALTER TABLE notifications_notification_documents
                    DROP CONSTRAINT document_id_refs_id_1844587e;

                ALTER TABLE notifications_notification_documents
                    DROP CONSTRAINT notification_id_refs_id_28e54e46;

                ALTER TABLE notifications_notification_submission_forms
                    DROP CONSTRAINT notifications_notification_submis_notification_id_15e80321_uniq;

                ALTER TABLE notifications_notification_submission_forms
                    DROP CONSTRAINT notification_id_refs_id_2945f2b;

                ALTER TABLE notifications_notification_submission_forms
                    DROP CONSTRAINT submissionform_id_refs_id_39ea865e;

                ALTER TABLE notifications_notificationanswer
                    DROP CONSTRAINT notification_id_refs_id_438d3c4b;

                ALTER TABLE notifications_notificationanswer
                    DROP CONSTRAINT pdf_document_id_refs_id_34905d91;

                ALTER TABLE notifications_progressreportnotification
                    DROP CONSTRAINT notification_ptr_id_refs_id_72e022ca;

                ALTER TABLE notifications_safetynotification
                    DROP CONSTRAINT notification_ptr_id_refs_id_33f4271d;

                ALTER TABLE notifications_safetynotification
                    DROP CONSTRAINT reviewer_id_refs_id_48bd6264;

                ALTER TABLE pki_certificate
                    DROP CONSTRAINT pki_certificate_cn_uniq;

                ALTER TABLE pki_certificate
                    DROP CONSTRAINT pki_certificate_serial_uniq;

                ALTER TABLE pki_certificate
                    DROP CONSTRAINT user_id_refs_id_301157f7;

                ALTER TABLE reversion_revision
                    DROP CONSTRAINT reversion_revision_user_id_fkey;

                ALTER TABLE reversion_version
                    DROP CONSTRAINT reversion_version_content_type_id_fkey;

                ALTER TABLE reversion_version
                    DROP CONSTRAINT reversion_version_revision_id_fkey;

                ALTER TABLE scratchpad_scratchpad
                    DROP CONSTRAINT scratchpad_scratchpad_owner_id_cda7ea0_uniq;

                ALTER TABLE scratchpad_scratchpad
                    DROP CONSTRAINT owner_id_refs_id_2c8e3d40;

                ALTER TABLE scratchpad_scratchpad
                    DROP CONSTRAINT submission_id_refs_id_5a63812;

                ALTER TABLE submission_registered_countries
                    DROP CONSTRAINT submission_registered_countries_submissionform_id_2d4f0860_uniq;

                ALTER TABLE submission_registered_countries
                    DROP CONSTRAINT country_id_refs_iso_64750829;

                ALTER TABLE submission_registered_countries
                    DROP CONSTRAINT submissionform_id_refs_id_4c14cc55;

                ALTER TABLE tasks_task
                    DROP CONSTRAINT assigned_to_id_refs_id_6ac564e8;

                ALTER TABLE tasks_task
                    DROP CONSTRAINT content_type_id_refs_id_26cb5864;

                ALTER TABLE tasks_task
                    DROP CONSTRAINT created_by_id_refs_id_6ac564e8;

                ALTER TABLE tasks_task
                    DROP CONSTRAINT task_type_id_refs_id_32d1bed7;

                ALTER TABLE tasks_task
                    DROP CONSTRAINT workflow_token_id_refs_id_427a1546;

                ALTER TABLE tasks_task_expedited_review_categories
                    DROP CONSTRAINT tasks_task_expedited_review_categories_task_id_79ab1a7_uniq;

                ALTER TABLE tasks_task_expedited_review_categories
                    DROP CONSTRAINT expeditedreviewcategory_id_refs_id_6eea492c;

                ALTER TABLE tasks_task_expedited_review_categories
                    DROP CONSTRAINT task_id_refs_id_6478e6a;

                ALTER TABLE tasks_tasktype
                    DROP CONSTRAINT workflow_node_id_refs_id_57a40ebe;

                ALTER TABLE tasks_tasktype_groups
                    DROP CONSTRAINT tasks_tasktype_groups_tasktype_id_48e20bc7_uniq;

                ALTER TABLE tasks_tasktype_groups
                    DROP CONSTRAINT group_id_refs_id_7c20a2fd;

                ALTER TABLE tasks_tasktype_groups
                    DROP CONSTRAINT tasktype_id_refs_id_133da373;

                ALTER TABLE users_invitation
                    DROP CONSTRAINT user_id_refs_id_12c4bbe6;

                ALTER TABLE users_loginhistory
                    DROP CONSTRAINT user_id_refs_id_6e169834;

                ALTER TABLE users_userprofile
                    DROP CONSTRAINT communication_proxy_id_refs_id_29ac45dc;

                ALTER TABLE users_userprofile
                    DROP CONSTRAINT user_id_refs_id_29ac45dc;

                ALTER TABLE users_usersettings
                    DROP CONSTRAINT user_id_refs_id_36d34e8f;

                ALTER TABLE votes_vote
                    DROP CONSTRAINT core_vote_top_id_key;

                ALTER TABLE votes_vote
                    DROP CONSTRAINT submission_form_id_refs_id_79396935;

                ALTER TABLE votes_vote
                    DROP CONSTRAINT top_id_refs_id_5784c4fd;

                ALTER TABLE votes_vote
                    DROP CONSTRAINT upgrade_for_id_refs_id_5d757b95;

                ALTER TABLE workflow_edge
                    DROP CONSTRAINT from_node_id_refs_id_5bb8b78a;

                ALTER TABLE workflow_edge
                    DROP CONSTRAINT guard_id_refs_id_4ae5fee6;

                ALTER TABLE workflow_edge
                    DROP CONSTRAINT to_node_id_refs_id_5bb8b78a;

                ALTER TABLE workflow_graph
                    DROP CONSTRAINT nodetype_ptr_id_refs_id_2447efd2;

                ALTER TABLE workflow_guard
                    DROP CONSTRAINT workflow_guard_content_type_id_5671ccb2_uniq;

                ALTER TABLE workflow_guard
                    DROP CONSTRAINT content_type_id_refs_id_780e1e19;

                ALTER TABLE workflow_node
                    DROP CONSTRAINT data_ct_id_refs_id_7e3a29;

                ALTER TABLE workflow_node
                    DROP CONSTRAINT graph_id_refs_nodetype_ptr_id_201be70c;

                ALTER TABLE workflow_node
                    DROP CONSTRAINT node_type_id_refs_id_57a88ec1;

                ALTER TABLE workflow_nodetype
                    DROP CONSTRAINT content_type_id_refs_id_2ccba443;

                ALTER TABLE workflow_nodetype
                    DROP CONSTRAINT data_type_id_refs_id_2ccba443;

                ALTER TABLE workflow_token
                    DROP CONSTRAINT consumed_by_id_refs_id_751151f7;

                ALTER TABLE workflow_token
                    DROP CONSTRAINT node_id_refs_id_3512bfb1;

                ALTER TABLE workflow_token
                    DROP CONSTRAINT source_id_refs_id_3512bfb1;

                ALTER TABLE workflow_token
                    DROP CONSTRAINT workflow_id_refs_id_11f2e720;

                ALTER TABLE workflow_token_trail
                    DROP CONSTRAINT workflow_token_trail_from_token_id_457148d1_uniq;

                ALTER TABLE workflow_token_trail
                    DROP CONSTRAINT from_token_id_refs_id_3339d7ee;

                ALTER TABLE workflow_token_trail
                    DROP CONSTRAINT to_token_id_refs_id_3339d7ee;

                ALTER TABLE workflow_workflow
                    DROP CONSTRAINT content_type_id_refs_id_57013600;

                ALTER TABLE workflow_workflow
                    DROP CONSTRAINT graph_id_refs_nodetype_ptr_id_7d146fe3;

                ALTER TABLE workflow_workflow
                    DROP CONSTRAINT parent_id_refs_id_43e7aa3e;

                DROP INDEX auth_group_permissions_group_id;
                DROP INDEX auth_group_permissions_permission_id;
                DROP INDEX auth_permission_content_type_id;
                DROP INDEX auth_user_groups_group_id;
                DROP INDEX auth_user_groups_user_id;
                DROP INDEX auth_user_user_permissions_permission_id;
                DROP INDEX auth_user_user_permissions_user_id;
                DROP INDEX billing_checklistbillingstate_billed_at;
                DROP INDEX billing_checklistpayment_checklists_checklist_id;
                DROP INDEX billing_checklistpayment_checklists_checklistpayment_id;
                DROP INDEX billing_invoice_submissions_invoice_id;
                DROP INDEX billing_invoice_submissions_submission_id;
                DROP INDEX boilerplate_text_author_id;
                DROP INDEX checklists_checklist_last_edited_by_id;
                DROP INDEX core_checklist_blueprint_id;
                DROP INDEX core_checklist_submission_id;
                DROP INDEX core_checklist_user_id;
                DROP INDEX core_checklistanswer_checklist_id;
                DROP INDEX core_checklistanswer_question_id;
                DROP INDEX core_checklistquestion_blueprint_id;
                DROP INDEX core_checklistquestion_index;
                DROP INDEX core_checklistquestion_number;
                DROP INDEX communication_message_rawmsg_digest_hex;
                DROP INDEX communication_message_rawmsg_digest_hex_like;
                DROP INDEX communication_message_rawmsg_msgid;
                DROP INDEX communication_message_rawmsg_msgid_like;
                DROP INDEX communication_message_receiver_id;
                DROP INDEX communication_message_reply_receiver_id;
                DROP INDEX communication_message_reply_to_id;
                DROP INDEX communication_message_sender_id;
                DROP INDEX communication_message_smtp_delivery_state;
                DROP INDEX communication_message_smtp_delivery_state_like;
                DROP INDEX communication_message_thread_id;
                DROP INDEX communication_message_uuid;
                DROP INDEX communication_message_uuid_like;
                DROP INDEX communication_thread_receiver_id;
                DROP INDEX communication_thread_related_thread_id;
                DROP INDEX communication_thread_sender_id;
                DROP INDEX communication_thread_submission_id;
                DROP INDEX communication_thread_task_id;
                DROP INDEX core_advancedsettings_default_contact_id;
                DROP INDEX core_expeditedreviewcategory_users_expeditedreviewcategory_id;
                DROP INDEX core_expeditedreviewcategory_users_user_id;
                DROP INDEX core_foreignparticipatingcenter_submission_form_id;
                DROP INDEX core_investigator_ethics_commission_id;
                DROP INDEX core_investigator_submission_form_id;
                DROP INDEX core_investigator_user_id;
                DROP INDEX core_investigatoremployee_investigator_id;
                DROP INDEX core_measure_submission_form_id;
                DROP INDEX core_medicalcategory_users_medicalcategory_id;
                DROP INDEX core_medicalcategory_users_user_id;
                DROP INDEX core_submission_billed_at;
                DROP INDEX core_submission_presenter_id;
                DROP INDEX core_submission_susar_presenter_id;
                DROP INDEX core_submission_workflow_lane;
                DROP INDEX core_submissionform_presenter_id;
                DROP INDEX core_submissionform_sponsor_id;
                DROP INDEX core_submissionform_submission_id;
                DROP INDEX core_submissionform_submitter_id;
                DROP INDEX core_nontesteduseddrug_submission_form_id;
                DROP INDEX core_submission_befangene_submission_id;
                DROP INDEX core_submission_befangene_user_id;
                DROP INDEX core_submission_expedited_review_categories_expeditedreviewcate;
                DROP INDEX core_submission_expedited_review_categories_submission_id;
                DROP INDEX core_submission_external_reviewers_submission_id;
                DROP INDEX core_submission_external_reviewers_user_id;
                DROP INDEX core_submission_medical_categories_medicalcategory_id;
                DROP INDEX core_submission_medical_categories_submission_id;
                DROP INDEX core_submissionform_documents_document_id;
                DROP INDEX core_submissionform_documents_submissionform_id;
                DROP INDEX core_submissionform_substance_p_c_t_countries_country_id;
                DROP INDEX core_submissionform_substance_p_c_t_countries_country_id_like;
                DROP INDEX core_submissionform_substance_p_c_t_countries_submissionform_id;
                DROP INDEX core_temporaryauthorization_submission_id;
                DROP INDEX core_temporaryauthorization_user_id;
                DROP INDEX django_admin_log_content_type_id;
                DROP INDEX django_admin_log_user_id;
                DROP INDEX docstash_docstash_content_type_id;
                DROP INDEX docstash_docstash_group;
                DROP INDEX docstash_docstash_group_like;
                DROP INDEX docstash_docstash_owner_id;
                DROP INDEX docstash_docstashdata_stash_id;
                DROP INDEX docstash_docstashdata_stash_id_like;
                DROP INDEX documents_document_content_type_id;
                DROP INDEX documents_document_doctype_id;
                DROP INDEX documents_document_replaces_document_id;
                DROP INDEX documents_documenttype_identifier;
                DROP INDEX documents_documenttype_identifier_like;
                DROP INDEX documents_downloadhistory_document_id;
                DROP INDEX documents_downloadhistory_user_id;
                DROP INDEX documents_downloadhistory_uuid;
                DROP INDEX documents_downloadhistory_uuid_like;
                DROP INDEX meetings_assignedmedicalcategory_board_member_id;
                DROP INDEX meetings_assignedmedicalcategory_category_id;
                DROP INDEX meetings_assignedmedicalcategory_meeting_id;
                DROP INDEX meetings_constraint_meeting_id;
                DROP INDEX meetings_constraint_user_id;
                DROP INDEX meetings_participation_entry_id;
                DROP INDEX meetings_participation_medical_category_id;
                DROP INDEX meetings_participation_user_id;
                DROP INDEX meetings_timetableentry_meeting_id;
                DROP INDEX meetings_timetableentry_submission_id;
                DROP INDEX notifications_amendmentnotification_new_submission_form_id;
                DROP INDEX notifications_amendmentnotification_old_submission_form_id;
                DROP INDEX notifications_notification_review_lane;
                DROP INDEX notifications_notification_review_lane_like;
                DROP INDEX notifications_notification_type_id;
                DROP INDEX notifications_notification_user_id;
                DROP INDEX notifications_notification_documents_document_id;
                DROP INDEX notifications_notification_documents_notification_id;
                DROP INDEX notifications_notification_submission_forms_notification_id;
                DROP INDEX notifications_notification_submission_forms_submissionform_id;
                DROP INDEX notifications_safetynotification_reviewer_id;
                DROP INDEX notifications_safetynotification_safety_type;
                DROP INDEX notifications_safetynotification_safety_type_like;
                DROP INDEX pki_certificate_user_id;
                DROP INDEX reversion_revision_user_id;
                DROP INDEX reversion_version_content_type_id;
                DROP INDEX reversion_version_revision_id;
                DROP INDEX scratchpad_scratchpad_owner_id;
                DROP INDEX scratchpad_scratchpad_submission_id;
                DROP INDEX submission_registered_countries_country_id;
                DROP INDEX submission_registered_countries_country_id_like;
                DROP INDEX submission_registered_countries_submissionform_id;
                DROP INDEX tasks_task_assigned_to_id;
                DROP INDEX tasks_task_content_type_id;
                DROP INDEX tasks_task_created_by_id;
                DROP INDEX tasks_task_task_type_id;
                DROP INDEX tasks_task_expedited_review_categories_expeditedreviewcategory_;
                DROP INDEX tasks_task_expedited_review_categories_task_id;
                DROP INDEX tasks_tasktype_groups_group_id;
                DROP INDEX tasks_tasktype_groups_tasktype_id;
                DROP INDEX users_invitation_user_id;
                DROP INDEX users_loginhistory_user_id;
                DROP INDEX users_userprofile_communication_proxy_id;
                DROP INDEX core_vote_submission_form_id;
                DROP INDEX workflow_edge_from_node_id;
                DROP INDEX workflow_edge_guard_id;
                DROP INDEX workflow_edge_to_node_id;
                DROP INDEX workflow_guard_content_type_id;
                DROP INDEX workflow_node_data_ct_id;
                DROP INDEX workflow_node_graph_id;
                DROP INDEX workflow_node_node_type_id;
                DROP INDEX workflow_nodetype_category;
                DROP INDEX workflow_nodetype_content_type_id;
                DROP INDEX workflow_nodetype_data_type_id;
                DROP INDEX workflow_token_consumed_by_id;
                DROP INDEX workflow_token_node_id;
                DROP INDEX workflow_token_source_id;
                DROP INDEX workflow_token_workflow_id;
                DROP INDEX workflow_token_trail_from_token_id;
                DROP INDEX workflow_token_trail_to_token_id;
                DROP INDEX workflow_workflow_content_type_id;
                DROP INDEX workflow_workflow_graph_id;
                DROP INDEX workflow_workflow_parent_id;

                ALTER TABLE notifications_completionreportnotification
                    ADD CONSTRAINT notifications_completionreportnotification_pkey PRIMARY KEY (notification_ptr_id);

                ALTER TABLE auth_group_permissions
                    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_key UNIQUE (group_id, permission_id);

                ALTER TABLE auth_group_permissions
                    ADD CONSTRAINT auth_group_permissio_group_id_689710a9a73b7457_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE auth_group_permissions
                    ADD CONSTRAINT auth_group_permission_id_1f49ccbbdc69d2fc_fk_auth_permission_id FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE auth_permission
                    ADD CONSTRAINT auth_permission_content_type_id_codename_key UNIQUE (content_type_id, codename);

                ALTER TABLE auth_permission
                    ADD CONSTRAINT auth_content_type_id_508cf46651277a81_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE auth_user_groups
                    ADD CONSTRAINT auth_user_groups_user_id_group_id_key UNIQUE (user_id, group_id);

                ALTER TABLE auth_user_groups
                    ADD CONSTRAINT auth_user_groups_group_id_33ac548dcf5f8e37_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE auth_user_groups
                    ADD CONSTRAINT auth_user_groups_user_id_4b5ed4ffdb8fd9b0_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE auth_user_user_permissions
                    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_key UNIQUE (user_id, permission_id);

                ALTER TABLE auth_user_user_permissions
                    ADD CONSTRAINT auth_user__permission_id_384b62483d7071f0_fk_auth_permission_id FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE auth_user_user_permissions
                    ADD CONSTRAINT auth_user_user_permiss_user_id_7f0938558328534a_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE billing_checklistbillingstate
                    ADD CONSTRAINT billing_checklist_id_398d8bf0ad00e26_fk_checklists_checklist_id FOREIGN KEY (checklist_id) REFERENCES checklists_checklist(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE billing_checklistpayment
                    ADD CONSTRAINT billing_c_document_id_12d090c23fbfb57f_fk_documents_document_id FOREIGN KEY (document_id) REFERENCES documents_document(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE billing_checklistpayment_checklists
                    ADD CONSTRAINT billing_checklistpayment_chec_checklistpayment_id_checklist_key UNIQUE (checklistpayment_id, checklist_id);

                ALTER TABLE billing_checklistpayment_checklists
                    ADD CONSTRAINT billin_checklist_id_177f911c9d7d1836_fk_checklists_checklist_id FOREIGN KEY (checklist_id) REFERENCES checklists_checklist(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE billing_checklistpayment_checklists
                    ADD CONSTRAINT e2394ea0507f18ea08c144f1480193d0 FOREIGN KEY (checklistpayment_id) REFERENCES billing_checklistpayment(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE billing_invoice
                    ADD CONSTRAINT billing_i_document_id_3f720058f73226dd_fk_documents_document_id FOREIGN KEY (document_id) REFERENCES documents_document(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE billing_invoice_submissions
                    ADD CONSTRAINT billing_invoice_submissions_invoice_id_submission_id_key UNIQUE (invoice_id, submission_id);

                ALTER TABLE billing_invoice_submissions
                    ADD CONSTRAINT billing_in_submission_id_3caf4637e0b15514_fk_core_submission_id FOREIGN KEY (submission_id) REFERENCES core_submission(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE billing_invoice_submissions
                    ADD CONSTRAINT billing_invoi_invoice_id_19987185de9fc34c_fk_billing_invoice_id FOREIGN KEY (invoice_id) REFERENCES billing_invoice(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE boilerplate_text
                    ADD CONSTRAINT boilerplate_text_slug_key UNIQUE (slug);

                ALTER TABLE boilerplate_text
                    ADD CONSTRAINT boilerplate_text_author_id_26d17c758656ce94_fk_auth_user_id FOREIGN KEY (author_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE checklists_checklist
                    ADD CONSTRAINT checklists_checklist_blueprint_id_5d7c407b5b54d3f7_uniq UNIQUE (blueprint_id, submission_id, user_id);

                ALTER TABLE checklists_checklist
                    ADD CONSTRAINT checklists_checklist_pdf_document_id_key UNIQUE (pdf_document_id);

                ALTER TABLE checklists_checklist
                    ADD CONSTRAINT "D54161cbc4eda6704139b3a561b0eeb4" FOREIGN KEY (blueprint_id) REFERENCES checklists_checklistblueprint(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE checklists_checklist
                    ADD CONSTRAINT check_pdf_document_id_1ce9dd2baa0b2bfe_fk_documents_document_id FOREIGN KEY (pdf_document_id) REFERENCES documents_document(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE checklists_checklist
                    ADD CONSTRAINT checklists_c_last_edited_by_id_25f6abeea6d183ca_fk_auth_user_id FOREIGN KEY (last_edited_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE checklists_checklist
                    ADD CONSTRAINT checklists_checklist_user_id_4d0a841611894097_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE checklists_checklist
                    ADD CONSTRAINT checklists_submission_id_4c401b9a1fa37fce_fk_core_submission_id FOREIGN KEY (submission_id) REFERENCES core_submission(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE checklists_checklistanswer
                    ADD CONSTRAINT "D08aba8236ef87ddc07c9a50bcc1d8fa" FOREIGN KEY (question_id) REFERENCES checklists_checklistquestion(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE checklists_checklistanswer
                    ADD CONSTRAINT checkl_checklist_id_1c17f049803c6d53_fk_checklists_checklist_id FOREIGN KEY (checklist_id) REFERENCES checklists_checklist(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE checklists_checklistblueprint
                    ADD CONSTRAINT checklists_checklistblueprint_slug_key UNIQUE (slug);

                ALTER TABLE checklists_checklistquestion
                    ADD CONSTRAINT checklists_checklistquestion_blueprint_id_92dc52b106a54a6_uniq UNIQUE (blueprint_id, number);

                ALTER TABLE checklists_checklistquestion
                    ADD CONSTRAINT "D4ff84969673d6ae94d340c0a80905c2" FOREIGN KEY (blueprint_id) REFERENCES checklists_checklistblueprint(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE communication_message
                    ADD CONSTRAINT commun_reply_to_id_10504d43f9dff04f_fk_communication_message_id FOREIGN KEY (reply_to_id) REFERENCES communication_message(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE communication_message
                    ADD CONSTRAINT communicat_thread_id_33357856a369e79_fk_communication_thread_id FOREIGN KEY (thread_id) REFERENCES communication_thread(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE communication_message
                    ADD CONSTRAINT communicatio_reply_receiver_id_1a1f656b9007dfa5_fk_auth_user_id FOREIGN KEY (reply_receiver_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE communication_message
                    ADD CONSTRAINT communication_mess_receiver_id_6d954b81f45761cc_fk_auth_user_id FOREIGN KEY (receiver_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE communication_message
                    ADD CONSTRAINT communication_messag_sender_id_5a625d5af585b386_fk_auth_user_id FOREIGN KEY (sender_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE communication_thread
                    ADD CONSTRAINT c_related_thread_id_437427f099f2302f_fk_communication_thread_id FOREIGN KEY (related_thread_id) REFERENCES communication_thread(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE communication_thread
                    ADD CONSTRAINT co_last_message_id_136814148104196b_fk_communication_message_id FOREIGN KEY (last_message_id) REFERENCES communication_message(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE communication_thread
                    ADD CONSTRAINT communicati_submission_id_7918f183b33b013_fk_core_submission_id FOREIGN KEY (submission_id) REFERENCES core_submission(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE communication_thread
                    ADD CONSTRAINT communication_threa_receiver_id_43519126a9fb2d6_fk_auth_user_id FOREIGN KEY (receiver_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE communication_thread
                    ADD CONSTRAINT communication_thread_sender_id_1f1dddbec57f107c_fk_auth_user_id FOREIGN KEY (sender_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE communication_thread
                    ADD CONSTRAINT communication_thread_task_id_5504c1f9f6d83afe_fk_tasks_task_id FOREIGN KEY (task_id) REFERENCES tasks_task(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_advancedsettings
                    ADD CONSTRAINT core_advance_default_contact_id_f23189bd01aafcb_fk_auth_user_id FOREIGN KEY (default_contact_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_expeditedreviewcategory
                    ADD CONSTRAINT core_expeditedreviewcategory_abbrev_key UNIQUE (abbrev);

                ALTER TABLE core_expeditedreviewcategory_users
                    ADD CONSTRAINT core_expeditedreviewcategory__expeditedreviewcategory_id_us_key UNIQUE (expeditedreviewcategory_id, user_id);

                ALTER TABLE core_expeditedreviewcategory_users
                    ADD CONSTRAINT "D1652d439d53949082efd663bddf155b" FOREIGN KEY (expeditedreviewcategory_id) REFERENCES core_expeditedreviewcategory(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_expeditedreviewcategory_users
                    ADD CONSTRAINT core_expeditedreviewca_user_id_642959801495e9e2_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_foreignparticipatingcenter
                    ADD CONSTRAINT co_submission_form_id_c61a3e7033d7c73_fk_core_submissionform_id FOREIGN KEY (submission_form_id) REFERENCES core_submissionform(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_investigator
                    ADD CONSTRAINT "D9e5cae137631c75e1589a387e083985" FOREIGN KEY (ethics_commission_id) REFERENCES core_ethicscommission(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_investigator
                    ADD CONSTRAINT c_submission_form_id_2b04ce915ac5d5ce_fk_core_submissionform_id FOREIGN KEY (submission_form_id) REFERENCES core_submissionform(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_investigator
                    ADD CONSTRAINT core_investigator_user_id_7e536a94e17cf925_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_investigatoremployee
                    ADD CONSTRAINT core_i_investigator_id_6a1136d8008deb4d_fk_core_investigator_id FOREIGN KEY (investigator_id) REFERENCES core_investigator(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_measure
                    ADD CONSTRAINT co_submission_form_id_2d43067671f37f4_fk_core_submissionform_id FOREIGN KEY (submission_form_id) REFERENCES core_submissionform(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_medicalcategory_users
                    ADD CONSTRAINT core_medicalcategory_users_medicalcategory_id_user_id_key UNIQUE (medicalcategory_id, user_id);

                ALTER TABLE core_medicalcategory_users
                    ADD CONSTRAINT core_medicalcategory_u_user_id_7cd358939438fd5f_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_medicalcategory_users
                    ADD CONSTRAINT medicalcategory_id_4a600090fcfd278e_fk_core_medicalcategory_id FOREIGN KEY (medicalcategory_id) REFERENCES core_medicalcategory(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submission
                    ADD CONSTRAINT "D451c3618f95c5f0901f3651e3aa786c" FOREIGN KEY (current_submission_form_id) REFERENCES core_submissionform(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submission
                    ADD CONSTRAINT core_submis_susar_presenter_id_2de5d266a873d331_fk_auth_user_id FOREIGN KEY (susar_presenter_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submission
                    ADD CONSTRAINT core_submission_presenter_id_35b1ab7a80044c14_fk_auth_user_id FOREIGN KEY (presenter_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submissionform
                    ADD CONSTRAINT core__current_pending_vote_id_72dbdec7dc4d5d3d_fk_votes_vote_id FOREIGN KEY (current_pending_vote_id) REFERENCES votes_vote(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submissionform
                    ADD CONSTRAINT core__pdf_document_id_46f6bff59da0e4cd_fk_documents_document_id FOREIGN KEY (pdf_document_id) REFERENCES documents_document(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submissionform
                    ADD CONSTRAINT core_current_published_vote_id_dc2c490e7900c1e_fk_votes_vote_id FOREIGN KEY (current_published_vote_id) REFERENCES votes_vote(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submissionform
                    ADD CONSTRAINT core_submi_submission_id_5019443784aef829_fk_core_submission_id FOREIGN KEY (submission_id) REFERENCES core_submission(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submissionform
                    ADD CONSTRAINT core_submissionfo_presenter_id_15e0f5f89d24707a_fk_auth_user_id FOREIGN KEY (presenter_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submissionform
                    ADD CONSTRAINT core_submissionfo_submitter_id_5b579c345b3b269d_fk_auth_user_id FOREIGN KEY (submitter_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submissionform
                    ADD CONSTRAINT core_submissionform_sponsor_id_53be4d69803b993e_fk_auth_user_id FOREIGN KEY (sponsor_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submissionform
                    ADD CONSTRAINT f767e1c34352b300bb5307915cae7a05 FOREIGN KEY (primary_investigator_id) REFERENCES core_investigator(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_nontesteduseddrug
                    ADD CONSTRAINT c_submission_form_id_6be8abc1c32f8c9f_fk_core_submissionform_id FOREIGN KEY (submission_form_id) REFERENCES core_submissionform(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submission_befangene
                    ADD CONSTRAINT core_submission_befangene_submission_id_user_id_key UNIQUE (submission_id, user_id);

                ALTER TABLE core_submission_befangene
                    ADD CONSTRAINT core_submis_submission_id_28b6433150fa79f_fk_core_submission_id FOREIGN KEY (submission_id) REFERENCES core_submission(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submission_befangene
                    ADD CONSTRAINT core_submission_befang_user_id_5eab13276b34d92a_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submission_expedited_review_categories
                    ADD CONSTRAINT core_submission_expedited_rev_submission_id_expeditedreview_key UNIQUE (submission_id, expeditedreviewcategory_id);

                ALTER TABLE core_submission_expedited_review_categories
                    ADD CONSTRAINT "D2dcab9b38c270880b3163458b602da0" FOREIGN KEY (expeditedreviewcategory_id) REFERENCES core_expeditedreviewcategory(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submission_expedited_review_categories
                    ADD CONSTRAINT core_submi_submission_id_527ad059b6326bfe_fk_core_submission_id FOREIGN KEY (submission_id) REFERENCES core_submission(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submission_external_reviewers
                    ADD CONSTRAINT core_submission_external_reviewers_submission_id_user_id_key UNIQUE (submission_id, user_id);

                ALTER TABLE core_submission_external_reviewers
                    ADD CONSTRAINT core_submi_submission_id_5c77aa41d42d08b5_fk_core_submission_id FOREIGN KEY (submission_id) REFERENCES core_submission(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submission_external_reviewers
                    ADD CONSTRAINT core_submission_extern_user_id_49088c57b360e866_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submission_medical_categories
                    ADD CONSTRAINT core_submission_medical_categ_submission_id_medicalcategory_key UNIQUE (submission_id, medicalcategory_id);

                ALTER TABLE core_submission_medical_categories
                    ADD CONSTRAINT core_submis_submission_id_dd2be1818094c67_fk_core_submission_id FOREIGN KEY (submission_id) REFERENCES core_submission(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submission_medical_categories
                    ADD CONSTRAINT medicalcategory_id_533b488220bee50f_fk_core_medicalcategory_id FOREIGN KEY (medicalcategory_id) REFERENCES core_medicalcategory(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submissionform_documents
                    ADD CONSTRAINT core_submissionform_documents_submissionform_id_document_id_key UNIQUE (submissionform_id, document_id);

                ALTER TABLE core_submissionform_documents
                    ADD CONSTRAINT co_submissionform_id_3da29ca6ff08ddee_fk_core_submissionform_id FOREIGN KEY (submissionform_id) REFERENCES core_submissionform(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submissionform_documents
                    ADD CONSTRAINT core_subm_document_id_6c470a23659160c5_fk_documents_document_id FOREIGN KEY (document_id) REFERENCES documents_document(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submissionform_substance_p_c_t_countries
                    ADD CONSTRAINT core_submissionform_substance__submissionform_id_country_id_key UNIQUE (submissionform_id, country_id);

                ALTER TABLE core_submissionform_substance_p_c_t_countries
                    ADD CONSTRAINT co_submissionform_id_13b59d64bf70287f_fk_core_submissionform_id FOREIGN KEY (submissionform_id) REFERENCES core_submissionform(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_submissionform_substance_p_c_t_countries
                    ADD CONSTRAINT core_submissionform__country_id_1ad378608429ac4a_fk_country_iso FOREIGN KEY (country_id) REFERENCES country(iso) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_temporaryauthorization
                    ADD CONSTRAINT core_tempo_submission_id_5ea5be3b37c16fe3_fk_core_submission_id FOREIGN KEY (submission_id) REFERENCES core_submission(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE core_temporaryauthorization
                    ADD CONSTRAINT core_temporaryauthoriz_user_id_60fb3b6a3acb706c_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE django_admin_log
                    ADD CONSTRAINT djan_content_type_id_697914295151027a_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE django_admin_log
                    ADD CONSTRAINT django_admin_log_user_id_52fdd58701c5f563_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE django_content_type
                    ADD CONSTRAINT django_content_type_app_label_45f3b1d93ec8c61c_uniq UNIQUE (app_label, model);

                ALTER TABLE docstash_docstash
                    ADD CONSTRAINT docstash_docstash_group_33395369aec8f8f4_uniq UNIQUE ("group", owner_id, content_type_id, object_id);

                ALTER TABLE docstash_docstash
                    ADD CONSTRAINT docs_content_type_id_74d9ca224c7d4b38_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE docstash_docstash
                    ADD CONSTRAINT docstash_docstash_owner_id_59aa3e4643dea616_fk_auth_user_id FOREIGN KEY (owner_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE docstash_docstashdata
                    ADD CONSTRAINT docstash_docstashdata_version_5a12a501976c894_uniq UNIQUE (version, stash_id);

                ALTER TABLE docstash_docstashdata
                    ADD CONSTRAINT docstash_doc_stash_id_1c86341e7bb48d6c_fk_docstash_docstash_key FOREIGN KEY (stash_id) REFERENCES docstash_docstash(key) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE documents_document
                    ADD CONSTRAINT documents_document_uuid_key UNIQUE (uuid);

                ALTER TABLE documents_document
                    ADD CONSTRAINT docum_content_type_id_be3cdaa70d32e64_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE documents_document
                    ADD CONSTRAINT docume_doctype_id_4c97ce585aa9a083_fk_documents_documenttype_id FOREIGN KEY (doctype_id) REFERENCES documents_documenttype(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE documents_document
                    ADD CONSTRAINT replaces_document_id_1cca8eddc83a8c36_fk_documents_document_id FOREIGN KEY (replaces_document_id) REFERENCES documents_document(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE documents_downloadhistory
                    ADD CONSTRAINT documents_document_id_641c9cc4dd87a28d_fk_documents_document_id FOREIGN KEY (document_id) REFERENCES documents_document(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE documents_downloadhistory
                    ADD CONSTRAINT documents_downloadhist_user_id_3db85b319c2ddb55_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE meetings_assignedmedicalcategory
                    ADD CONSTRAINT meetings_assignedmedicalcatego_category_id_52b7232b940f594_uniq UNIQUE (category_id, meeting_id);

                ALTER TABLE meetings_assignedmedicalcategory
                    ADD CONSTRAINT meeting_category_id_3f4a9d4f4a3f26e0_fk_core_medicalcategory_id FOREIGN KEY (category_id) REFERENCES core_medicalcategory(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE meetings_assignedmedicalcategory
                    ADD CONSTRAINT meetings_ass_meeting_id_70d727daa7efb1e4_fk_meetings_meeting_id FOREIGN KEY (meeting_id) REFERENCES meetings_meeting(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE meetings_assignedmedicalcategory
                    ADD CONSTRAINT meetings_assig_board_member_id_52dbb47945b5f919_fk_auth_user_id FOREIGN KEY (board_member_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE meetings_constraint
                    ADD CONSTRAINT meetings_con_meeting_id_4450b071d20e2171_fk_meetings_meeting_id FOREIGN KEY (meeting_id) REFERENCES meetings_meeting(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE meetings_constraint
                    ADD CONSTRAINT meetings_constraint_user_id_1c31862a07454a4c_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE meetings_participation
                    ADD CONSTRAINT ce6fd2b38bb7d5648398fb7cdc28a82c FOREIGN KEY (medical_category_id) REFERENCES core_medicalcategory(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE meetings_participation
                    ADD CONSTRAINT meeting_entry_id_1c046428ae83dedf_fk_meetings_timetableentry_id FOREIGN KEY (entry_id) REFERENCES meetings_timetableentry(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE meetings_participation
                    ADD CONSTRAINT meetings_participation_user_id_5d7614bfd7b0ef8f_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE meetings_timetableentry
                    ADD CONSTRAINT meetings_timetableentry_meeting_id_7591dd39f75db60b_uniq UNIQUE (meeting_id, timetable_index);

                ALTER TABLE meetings_timetableentry
                    ADD CONSTRAINT meetings_t_submission_id_2be389d2d3cf7d2f_fk_core_submission_id FOREIGN KEY (submission_id) REFERENCES core_submission(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE meetings_timetableentry
                    ADD CONSTRAINT meetings_time_meeting_id_e773e49178ff4a3_fk_meetings_meeting_id FOREIGN KEY (meeting_id) REFERENCES meetings_meeting(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE notifications_amendmentnotification
                    ADD CONSTRAINT "D44f3178c97857a97860648870bf86e9" FOREIGN KEY (new_submission_form_id) REFERENCES core_submissionform(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE notifications_amendmentnotification
                    ADD CONSTRAINT "D5853b7b699e044bac37f4c1d7d46eeb" FOREIGN KEY (old_submission_form_id) REFERENCES core_submissionform(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE notifications_amendmentnotification
                    ADD CONSTRAINT b268c69cc0fb4f9db1427ca92050c3b4 FOREIGN KEY (notification_ptr_id) REFERENCES notifications_notification(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE notifications_completionreportnotification
                    ADD CONSTRAINT "D0503b1f7e8b5c75b36ec102d4494aef" FOREIGN KEY (notification_ptr_id) REFERENCES notifications_notification(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE notifications_notification
                    ADD CONSTRAINT n_type_id_35e62d16432cde5e_fk_notifications_notificationtype_id FOREIGN KEY (type_id) REFERENCES notifications_notificationtype(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE notifications_notification
                    ADD CONSTRAINT notif_pdf_document_id_7b26c69484f5ece0_fk_documents_document_id FOREIGN KEY (pdf_document_id) REFERENCES documents_document(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE notifications_notification
                    ADD CONSTRAINT notifications_notifica_user_id_5506ddee4eaa1195_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE notifications_notification_documents
                    ADD CONSTRAINT notifications_notification_docu_notification_id_document_id_key UNIQUE (notification_id, document_id);

                ALTER TABLE notifications_notification_documents
                    ADD CONSTRAINT c20b15fe5b38aeb92a11c968f2e6c874 FOREIGN KEY (notification_id) REFERENCES notifications_notification(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE notifications_notification_documents
                    ADD CONSTRAINT notificati_document_id_6d8f3297eb26348_fk_documents_document_id FOREIGN KEY (document_id) REFERENCES documents_document(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE notifications_notification_submission_forms
                    ADD CONSTRAINT notifications_notification_su_notification_id_submissionfor_key UNIQUE (notification_id, submissionform_id);

                ALTER TABLE notifications_notification_submission_forms
                    ADD CONSTRAINT "D14544f2e602bac2cf76cb4f469ac5ba" FOREIGN KEY (notification_id) REFERENCES notifications_notification(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE notifications_notification_submission_forms
                    ADD CONSTRAINT no_submissionform_id_281f1a77d79e00c0_fk_core_submissionform_id FOREIGN KEY (submissionform_id) REFERENCES core_submissionform(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE notifications_notificationanswer
                    ADD CONSTRAINT "D09f01b286740ec068bca2316c863bf4" FOREIGN KEY (notification_id) REFERENCES notifications_notification(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE notifications_notificationanswer
                    ADD CONSTRAINT notif_pdf_document_id_698f9302335f8c40_fk_documents_document_id FOREIGN KEY (pdf_document_id) REFERENCES documents_document(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE notifications_progressreportnotification
                    ADD CONSTRAINT "D60deb9568d087372c29b4f11f37b79a" FOREIGN KEY (notification_ptr_id) REFERENCES notifications_notification(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE notifications_safetynotification
                    ADD CONSTRAINT "D9c4dcfa48424b5f3d8ac8a243d78d3d" FOREIGN KEY (notification_ptr_id) REFERENCES notifications_notification(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE notifications_safetynotification
                    ADD CONSTRAINT notifications_safe_reviewer_id_50e94f49a02c11af_fk_auth_user_id FOREIGN KEY (reviewer_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE pki_certificate
                    ADD CONSTRAINT pki_certificate_cn_key UNIQUE (cn);

                ALTER TABLE pki_certificate
                    ADD CONSTRAINT pki_certificate_serial_key UNIQUE (serial);

                ALTER TABLE pki_certificate
                    ADD CONSTRAINT pki_certificate_user_id_23bdea4671178638_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE reversion_revision
                    ADD CONSTRAINT reversion_revision_user_id_53d027e45b2ec55e_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE reversion_version
                    ADD CONSTRAINT rever_content_type_id_c01a11926d4c4a9_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE reversion_version
                    ADD CONSTRAINT reversion__revision_id_48ec3744916a950_fk_reversion_revision_id FOREIGN KEY (revision_id) REFERENCES reversion_revision(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE scratchpad_scratchpad
                    ADD CONSTRAINT scratchpad_scratchpad_owner_id_7afc65cef3258160_uniq UNIQUE (owner_id, submission_id);

                ALTER TABLE scratchpad_scratchpad
                    ADD CONSTRAINT scratchpad_scratchpad_owner_id_7808fc7fb129e52_fk_auth_user_id FOREIGN KEY (owner_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE scratchpad_scratchpad
                    ADD CONSTRAINT scratchpad_submission_id_79e5c1deb6b38008_fk_core_submission_id FOREIGN KEY (submission_id) REFERENCES core_submission(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE submission_registered_countries
                    ADD CONSTRAINT submission_registered_countrie_submissionform_id_country_id_key UNIQUE (submissionform_id, country_id);

                ALTER TABLE submission_registered_countries
                    ADD CONSTRAINT su_submissionform_id_73432f721a2016c3_fk_core_submissionform_id FOREIGN KEY (submissionform_id) REFERENCES core_submissionform(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE submission_registered_countries
                    ADD CONSTRAINT submission_registere_country_id_3bce23ecf6104140_fk_country_iso FOREIGN KEY (country_id) REFERENCES country(iso) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE tasks_task
                    ADD CONSTRAINT task_content_type_id_645d54bfc5906b3c_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE tasks_task
                    ADD CONSTRAINT tasks_t_workflow_token_id_55d0e32ed378a0fd_fk_workflow_token_id FOREIGN KEY (workflow_token_id) REFERENCES workflow_token(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE tasks_task
                    ADD CONSTRAINT tasks_task_assigned_to_id_492fa3ac6f6fcc7d_fk_auth_user_id FOREIGN KEY (assigned_to_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE tasks_task
                    ADD CONSTRAINT tasks_task_created_by_id_7db9e111f94d96e8_fk_auth_user_id FOREIGN KEY (created_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE tasks_task
                    ADD CONSTRAINT tasks_task_task_type_id_391cdd62970e6caf_fk_tasks_tasktype_id FOREIGN KEY (task_type_id) REFERENCES tasks_tasktype(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE tasks_task_expedited_review_categories
                    ADD CONSTRAINT tasks_task_expedited_review_c_task_id_expeditedreviewcatego_key UNIQUE (task_id, expeditedreviewcategory_id);

                ALTER TABLE tasks_task_expedited_review_categories
                    ADD CONSTRAINT a83c913f7fe6dde605aa84bf1770bf49 FOREIGN KEY (expeditedreviewcategory_id) REFERENCES core_expeditedreviewcategory(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE tasks_task_expedited_review_categories
                    ADD CONSTRAINT tasks_task_expedited__task_id_6e1b030371830dc8_fk_tasks_task_id FOREIGN KEY (task_id) REFERENCES tasks_task(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE tasks_tasktype
                    ADD CONSTRAINT tasks_tas_workflow_node_id_16d637b6b688961d_fk_workflow_node_id FOREIGN KEY (workflow_node_id) REFERENCES workflow_node(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE tasks_tasktype_groups
                    ADD CONSTRAINT tasks_tasktype_groups_tasktype_id_group_id_key UNIQUE (tasktype_id, group_id);

                ALTER TABLE tasks_tasktype_groups
                    ADD CONSTRAINT tasks_tasktyp_tasktype_id_412ec931d66aaef1_fk_tasks_tasktype_id FOREIGN KEY (tasktype_id) REFERENCES tasks_tasktype(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE tasks_tasktype_groups
                    ADD CONSTRAINT tasks_tasktype_group_group_id_173a50c0630d02aa_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE users_invitation
                    ADD CONSTRAINT users_invitation_user_id_2213deb7d02c7bb3_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE users_loginhistory
                    ADD CONSTRAINT users_loginhistory_user_id_73caa4f0febf9eb3_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE users_userprofile
                    ADD CONSTRAINT users_u_communication_proxy_id_70fc48eecc9ff714_fk_auth_user_id FOREIGN KEY (communication_proxy_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE users_userprofile
                    ADD CONSTRAINT users_userprofile_user_id_5c10ccd727779b5d_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE users_usersettings
                    ADD CONSTRAINT users_usersettings_user_id_1e1ad0683d0e8330_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE votes_vote
                    ADD CONSTRAINT votes_vote_top_id_key UNIQUE (top_id);

                ALTER TABLE votes_vote
                    ADD CONSTRAINT v_submission_form_id_5e7d8cf55b97af5c_fk_core_submissionform_id FOREIGN KEY (submission_form_id) REFERENCES core_submissionform(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE votes_vote
                    ADD CONSTRAINT votes_vot_top_id_33fa6ba54ad1c6a8_fk_meetings_timetableentry_id FOREIGN KEY (top_id) REFERENCES meetings_timetableentry(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE votes_vote
                    ADD CONSTRAINT votes_vote_upgrade_for_id_18a418de37470ad9_fk_votes_vote_id FOREIGN KEY (upgrade_for_id) REFERENCES votes_vote(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_edge
                    ADD CONSTRAINT workflow_edge_from_node_id_2a8a906e73d3c4dc_fk_workflow_node_id FOREIGN KEY (from_node_id) REFERENCES workflow_node(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_edge
                    ADD CONSTRAINT workflow_edge_guard_id_41a3db37bb002730_fk_workflow_guard_id FOREIGN KEY (guard_id) REFERENCES workflow_guard(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_edge
                    ADD CONSTRAINT workflow_edge_to_node_id_7e159c16829d279b_fk_workflow_node_id FOREIGN KEY (to_node_id) REFERENCES workflow_node(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_graph
                    ADD CONSTRAINT workfl_nodetype_ptr_id_50a2827dfa2d461d_fk_workflow_nodetype_id FOREIGN KEY (nodetype_ptr_id) REFERENCES workflow_nodetype(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_guard
                    ADD CONSTRAINT workflow_guard_content_type_id_149ae8d95671ccb2_uniq UNIQUE (content_type_id, implementation);

                ALTER TABLE workflow_guard
                    ADD CONSTRAINT work_content_type_id_57541a75f70eba79_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_node
                    ADD CONSTRAINT wor_graph_id_4f76757c8ffb38f4_fk_workflow_graph_nodetype_ptr_id FOREIGN KEY (graph_id) REFERENCES workflow_graph(nodetype_ptr_id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_node
                    ADD CONSTRAINT workflow__data_ct_id_3d3b3aa94aad8c4c_fk_django_content_type_id FOREIGN KEY (data_ct_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_node
                    ADD CONSTRAINT workflow__node_type_id_6524e29a668f6abd_fk_workflow_nodetype_id FOREIGN KEY (node_type_id) REFERENCES workflow_nodetype(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_nodetype
                    ADD CONSTRAINT work_content_type_id_21d35ece29601f5d_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_nodetype
                    ADD CONSTRAINT workflow_data_type_id_ef1cad566bb3f53_fk_django_content_type_id FOREIGN KEY (data_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_token
                    ADD CONSTRAINT workflow_t_workflow_id_5fe8a4b6cb599686_fk_workflow_workflow_id FOREIGN KEY (workflow_id) REFERENCES workflow_workflow(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_token
                    ADD CONSTRAINT workflow_token_consumed_by_id_4bdffce12990dc30_fk_auth_user_id FOREIGN KEY (consumed_by_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_token
                    ADD CONSTRAINT workflow_token_node_id_5158b93abd1831a9_fk_workflow_node_id FOREIGN KEY (node_id) REFERENCES workflow_node(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_token
                    ADD CONSTRAINT workflow_token_source_id_86892c45a506e6c_fk_workflow_node_id FOREIGN KEY (source_id) REFERENCES workflow_node(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_token_trail
                    ADD CONSTRAINT workflow_token_trail_from_token_id_to_token_id_key UNIQUE (from_token_id, to_token_id);

                ALTER TABLE workflow_token_trail
                    ADD CONSTRAINT workflow_tok_from_token_id_5fd5db637ff7c2a_fk_workflow_token_id FOREIGN KEY (from_token_id) REFERENCES workflow_token(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_token_trail
                    ADD CONSTRAINT workflow_toke_to_token_id_1f57b4a9ce7256c5_fk_workflow_token_id FOREIGN KEY (to_token_id) REFERENCES workflow_token(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_workflow
                    ADD CONSTRAINT wor_graph_id_6264e97b7705f01d_fk_workflow_graph_nodetype_ptr_id FOREIGN KEY (graph_id) REFERENCES workflow_graph(nodetype_ptr_id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_workflow
                    ADD CONSTRAINT work_content_type_id_33325746d5d97260_fk_django_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE workflow_workflow
                    ADD CONSTRAINT workflow_workfl_parent_id_3376a49cff10e5dc_fk_workflow_token_id FOREIGN KEY (parent_id) REFERENCES workflow_token(id) DEFERRABLE INITIALLY DEFERRED;

                CREATE INDEX auth_group_name_253ae2a6331666e8_like ON auth_group USING btree (name varchar_pattern_ops);

                CREATE INDEX auth_group_permissions_0e939a4f ON auth_group_permissions USING btree (group_id);

                CREATE INDEX auth_group_permissions_8373b171 ON auth_group_permissions USING btree (permission_id);

                CREATE INDEX auth_permission_417f1b1c ON auth_permission USING btree (content_type_id);

                CREATE INDEX auth_user_username_51b3b110094b8aae_like ON auth_user USING btree (username varchar_pattern_ops);

                CREATE INDEX auth_user_groups_0e939a4f ON auth_user_groups USING btree (group_id);

                CREATE INDEX auth_user_groups_e8701ad4 ON auth_user_groups USING btree (user_id);

                CREATE INDEX auth_user_user_permissions_8373b171 ON auth_user_user_permissions USING btree (permission_id);

                CREATE INDEX auth_user_user_permissions_e8701ad4 ON auth_user_user_permissions USING btree (user_id);

                CREATE INDEX billing_checklistbillingstate_88cf3f27 ON billing_checklistbillingstate USING btree (billed_at);

                CREATE INDEX billing_checklistpayment_checklists_690b1cb8 ON billing_checklistpayment_checklists USING btree (checklist_id);

                CREATE INDEX billing_checklistpayment_checklists_c58d9763 ON billing_checklistpayment_checklists USING btree (checklistpayment_id);

                CREATE INDEX billing_invoice_submissions_1dd9cfcc ON billing_invoice_submissions USING btree (submission_id);

                CREATE INDEX billing_invoice_submissions_f1f5d967 ON billing_invoice_submissions USING btree (invoice_id);

                CREATE INDEX boilerplate_text_4f331e2f ON boilerplate_text USING btree (author_id);

                CREATE INDEX boilerplate_text_slug_15aeefd7f4072b1d_like ON boilerplate_text USING btree (slug varchar_pattern_ops);

                CREATE INDEX celery_taskmeta_task_id_like ON celery_taskmeta USING btree (task_id varchar_pattern_ops);

                CREATE INDEX celery_tasksetmeta_taskset_id_like ON celery_tasksetmeta USING btree (taskset_id varchar_pattern_ops);

                CREATE INDEX checklists_checklist_1dd9cfcc ON checklists_checklist USING btree (submission_id);

                CREATE INDEX checklists_checklist_2c682e13 ON checklists_checklist USING btree (blueprint_id);

                CREATE INDEX checklists_checklist_87f04f9b ON checklists_checklist USING btree (last_edited_by_id);

                CREATE INDEX checklists_checklist_e8701ad4 ON checklists_checklist USING btree (user_id);

                CREATE INDEX checklists_checklistanswer_690b1cb8 ON checklists_checklistanswer USING btree (checklist_id);

                CREATE INDEX checklists_checklistanswer_7aa0f6ee ON checklists_checklistanswer USING btree (question_id);

                CREATE INDEX checklists_checklistblueprint_slug_18951bd8315dd1e6_like ON checklists_checklistblueprint USING btree (slug varchar_pattern_ops);

                CREATE INDEX checklists_checklistquestion_2c682e13 ON checklists_checklistquestion USING btree (blueprint_id);

                CREATE INDEX checklists_checklistquestion_6a992d55 ON checklists_checklistquestion USING btree (index);

                CREATE INDEX checklists_checklistquestion_b1bc248a ON checklists_checklistquestion USING btree (number);

                CREATE INDEX checklists_checklistquestion_number_444b6eb92db84726_like ON checklists_checklistquestion USING btree (number varchar_pattern_ops);

                CREATE INDEX communication_message_6bc858a1 ON communication_message USING btree (rawmsg_msgid);

                CREATE INDEX communication_message_6ec85d95 ON communication_message USING btree (reply_to_id);

                CREATE INDEX communication_message_9218a9c4 ON communication_message USING btree (rawmsg_digest_hex);

                CREATE INDEX communication_message_924b1846 ON communication_message USING btree (sender_id);

                CREATE INDEX communication_message_d31f921e ON communication_message USING btree (reply_receiver_id);

                CREATE INDEX communication_message_d41c2251 ON communication_message USING btree (receiver_id);

                CREATE INDEX communication_message_e3464c97 ON communication_message USING btree (thread_id);

                CREATE INDEX communication_message_ef7c876f ON communication_message USING btree (uuid);

                CREATE INDEX communication_message_f1700b5a ON communication_message USING btree (smtp_delivery_state);

                CREATE INDEX communication_message_rawmsg_digest_hex_3a5f10c885713657_like ON communication_message USING btree (rawmsg_digest_hex varchar_pattern_ops);

                CREATE INDEX communication_message_rawmsg_msgid_4878d6c1be01dd52_like ON communication_message USING btree (rawmsg_msgid varchar_pattern_ops);

                CREATE INDEX communication_message_smtp_delivery_state_1a33f79f3f98185c_like ON communication_message USING btree (smtp_delivery_state varchar_pattern_ops);

                CREATE INDEX communication_message_uuid_6dc940fb482cf6d5_like ON communication_message USING btree (uuid varchar_pattern_ops);

                CREATE INDEX communication_thread_1dd9cfcc ON communication_thread USING btree (submission_id);

                CREATE INDEX communication_thread_57746cc8 ON communication_thread USING btree (task_id);

                CREATE INDEX communication_thread_924b1846 ON communication_thread USING btree (sender_id);

                CREATE INDEX communication_thread_ca5646ce ON communication_thread USING btree (related_thread_id);

                CREATE INDEX communication_thread_d41c2251 ON communication_thread USING btree (receiver_id);

                CREATE INDEX core_advancedsettings_9e89e40f ON core_advancedsettings USING btree (default_contact_id);

                CREATE INDEX core_expeditedreviewcategory_abbrev_f4b17b59a74391_like ON core_expeditedreviewcategory USING btree (abbrev varchar_pattern_ops);

                CREATE INDEX core_expeditedreviewcategory_users_b15936f1 ON core_expeditedreviewcategory_users USING btree (expeditedreviewcategory_id);

                CREATE INDEX core_expeditedreviewcategory_users_e8701ad4 ON core_expeditedreviewcategory_users USING btree (user_id);

                CREATE INDEX core_foreignparticipatingcenter_abde9629 ON core_foreignparticipatingcenter USING btree (submission_form_id);

                CREATE INDEX core_investigator_16ce9133 ON core_investigator USING btree (ethics_commission_id);

                CREATE INDEX core_investigator_abde9629 ON core_investigator USING btree (submission_form_id);

                CREATE INDEX core_investigator_e8701ad4 ON core_investigator USING btree (user_id);

                CREATE INDEX core_investigatoremployee_a59df775 ON core_investigatoremployee USING btree (investigator_id);

                CREATE INDEX core_measure_abde9629 ON core_measure USING btree (submission_form_id);

                CREATE INDEX core_medicalcategory_abbrev_363af0ad75f08ed4_like ON core_medicalcategory USING btree (abbrev varchar_pattern_ops);

                CREATE INDEX core_medicalcategory_users_888767d0 ON core_medicalcategory_users USING btree (medicalcategory_id);

                CREATE INDEX core_medicalcategory_users_e8701ad4 ON core_medicalcategory_users USING btree (user_id);

                CREATE INDEX core_submission_15842be0 ON core_submission USING btree (workflow_lane);

                CREATE INDEX core_submission_56ee8882 ON core_submission USING btree (susar_presenter_id);

                CREATE INDEX core_submission_88cf3f27 ON core_submission USING btree (billed_at);

                CREATE INDEX core_submission_9fc38942 ON core_submission USING btree (presenter_id);

                CREATE INDEX core_submissionform_1dd9cfcc ON core_submissionform USING btree (submission_id);

                CREATE INDEX core_submissionform_42545d36 ON core_submissionform USING btree (sponsor_id);

                CREATE INDEX core_submissionform_9fc38942 ON core_submissionform USING btree (presenter_id);

                CREATE INDEX core_submissionform_a8919bbb ON core_submissionform USING btree (submitter_id);

                CREATE INDEX core_nontesteduseddrug_abde9629 ON core_nontesteduseddrug USING btree (submission_form_id);

                CREATE INDEX core_submission_befangene_1dd9cfcc ON core_submission_befangene USING btree (submission_id);

                CREATE INDEX core_submission_befangene_e8701ad4 ON core_submission_befangene USING btree (user_id);

                CREATE INDEX core_submission_expedited_review_categories_1dd9cfcc ON core_submission_expedited_review_categories USING btree (submission_id);

                CREATE INDEX core_submission_expedited_review_categories_b15936f1 ON core_submission_expedited_review_categories USING btree (expeditedreviewcategory_id);

                CREATE INDEX core_submission_external_reviewers_1dd9cfcc ON core_submission_external_reviewers USING btree (submission_id);

                CREATE INDEX core_submission_external_reviewers_e8701ad4 ON core_submission_external_reviewers USING btree (user_id);

                CREATE INDEX core_submission_medical_categories_1dd9cfcc ON core_submission_medical_categories USING btree (submission_id);

                CREATE INDEX core_submission_medical_categories_888767d0 ON core_submission_medical_categories USING btree (medicalcategory_id);

                CREATE INDEX core_submissionform_documents_d1fbd48c ON core_submissionform_documents USING btree (submissionform_id);

                CREATE INDEX core_submissionform_documents_e7fafc10 ON core_submissionform_documents USING btree (document_id);

                CREATE INDEX core_submissionform_substance__country_id_1ad378608429ac4a_like ON core_submissionform_substance_p_c_t_countries USING btree (country_id varchar_pattern_ops);

                CREATE INDEX core_submissionform_substance_p_c_t_countries_93bfec8a ON core_submissionform_substance_p_c_t_countries USING btree (country_id);

                CREATE INDEX core_submissionform_substance_p_c_t_countries_d1fbd48c ON core_submissionform_substance_p_c_t_countries USING btree (submissionform_id);

                CREATE INDEX core_temporaryauthorization_1dd9cfcc ON core_temporaryauthorization USING btree (submission_id);

                CREATE INDEX core_temporaryauthorization_e8701ad4 ON core_temporaryauthorization USING btree (user_id);

                CREATE INDEX country_iso_like ON country USING btree (iso varchar_pattern_ops);

                CREATE INDEX django_admin_log_417f1b1c ON django_admin_log USING btree (content_type_id);

                CREATE INDEX django_admin_log_e8701ad4 ON django_admin_log USING btree (user_id);

                CREATE INDEX django_session_de54fa62 ON django_session USING btree (expire_date);

                CREATE INDEX django_session_session_key_461cfeaa630ca218_like ON django_session USING btree (session_key varchar_pattern_ops);

                CREATE INDEX djcelery_periodictask_name_like ON djcelery_periodictask USING btree (name varchar_pattern_ops);

                CREATE INDEX djcelery_taskstate_task_id_like ON djcelery_taskstate USING btree (task_id varchar_pattern_ops);

                CREATE INDEX djcelery_workerstate_hostname_like ON djcelery_workerstate USING btree (hostname varchar_pattern_ops);

                CREATE INDEX docstash_docstash_417f1b1c ON docstash_docstash USING btree (content_type_id);

                CREATE INDEX docstash_docstash_5e7b1936 ON docstash_docstash USING btree (owner_id);

                CREATE INDEX docstash_docstash_db0f6f37 ON docstash_docstash USING btree ("group");

                CREATE INDEX docstash_docstash_group_7d22c42e4d17d8db_like ON docstash_docstash USING btree ("group" varchar_pattern_ops);

                CREATE INDEX docstash_docstash_key_3732b391db1aea7b_like ON docstash_docstash USING btree (key varchar_pattern_ops);

                CREATE INDEX docstash_docstashdata_8fc32603 ON docstash_docstashdata USING btree (stash_id);

                CREATE INDEX docstash_docstashdata_stash_id_1c86341e7bb48d6c_like ON docstash_docstashdata USING btree (stash_id varchar_pattern_ops);

                CREATE INDEX documents_document_417f1b1c ON documents_document USING btree (content_type_id);

                CREATE INDEX documents_document_795d4df1 ON documents_document USING btree (replaces_document_id);

                CREATE INDEX documents_document_d4f20e7a ON documents_document USING btree (doctype_id);

                CREATE INDEX documents_document_uuid_5ea1d842009c435c_like ON documents_document USING btree (uuid varchar_pattern_ops);

                CREATE INDEX documents_documenttype_f393f3f5 ON documents_documenttype USING btree (identifier);

                CREATE INDEX documents_documenttype_identifier_7d9ea8d4ae24eff2_like ON documents_documenttype USING btree (identifier varchar_pattern_ops);

                CREATE INDEX documents_downloadhistory_e7fafc10 ON documents_downloadhistory USING btree (document_id);

                CREATE INDEX documents_downloadhistory_e8701ad4 ON documents_downloadhistory USING btree (user_id);

                CREATE INDEX documents_downloadhistory_ef7c876f ON documents_downloadhistory USING btree (uuid);

                CREATE INDEX documents_downloadhistory_uuid_5b513ca03b5fc4f2_like ON documents_downloadhistory USING btree (uuid varchar_pattern_ops);

                CREATE INDEX meetings_assignedmedicalcategory_383440d3 ON meetings_assignedmedicalcategory USING btree (meeting_id);

                CREATE INDEX meetings_assignedmedicalcategory_532157e3 ON meetings_assignedmedicalcategory USING btree (board_member_id);

                CREATE INDEX meetings_assignedmedicalcategory_b583a629 ON meetings_assignedmedicalcategory USING btree (category_id);

                CREATE INDEX meetings_constraint_383440d3 ON meetings_constraint USING btree (meeting_id);

                CREATE INDEX meetings_constraint_e8701ad4 ON meetings_constraint USING btree (user_id);

                CREATE INDEX meetings_participation_8aa907c1 ON meetings_participation USING btree (medical_category_id);

                CREATE INDEX meetings_participation_b64a62ea ON meetings_participation USING btree (entry_id);

                CREATE INDEX meetings_participation_e8701ad4 ON meetings_participation USING btree (user_id);

                CREATE INDEX meetings_timetableentry_1dd9cfcc ON meetings_timetableentry USING btree (submission_id);

                CREATE INDEX meetings_timetableentry_383440d3 ON meetings_timetableentry USING btree (meeting_id);

                CREATE INDEX notifications_amendmentnotification_3a33df24 ON notifications_amendmentnotification USING btree (old_submission_form_id);

                CREATE INDEX notifications_amendmentnotification_dec60fd6 ON notifications_amendmentnotification USING btree (new_submission_form_id);

                CREATE INDEX notifications_notification_4fffab2f ON notifications_notification USING btree (review_lane);

                CREATE INDEX notifications_notification_94757cae ON notifications_notification USING btree (type_id);

                CREATE INDEX notifications_notification_e8701ad4 ON notifications_notification USING btree (user_id);

                CREATE INDEX notifications_notification_review_lane_67d6a99b924ffc41_like ON notifications_notification USING btree (review_lane varchar_pattern_ops);

                CREATE INDEX notifications_notification_documents_53fb5b6b ON notifications_notification_documents USING btree (notification_id);

                CREATE INDEX notifications_notification_documents_e7fafc10 ON notifications_notification_documents USING btree (document_id);

                CREATE INDEX notifications_notification_submission_forms_53fb5b6b ON notifications_notification_submission_forms USING btree (notification_id);

                CREATE INDEX notifications_notification_submission_forms_d1fbd48c ON notifications_notification_submission_forms USING btree (submissionform_id);

                CREATE INDEX notifications_notificationtype_name_2da51767be0f29ac_like ON notifications_notificationtype USING btree (name varchar_pattern_ops);

                CREATE INDEX notifications_safetynotificat_safety_type_7f1ae4c6813625e9_like ON notifications_safetynotification USING btree (safety_type varchar_pattern_ops);

                CREATE INDEX notifications_safetynotification_071d8141 ON notifications_safetynotification USING btree (reviewer_id);

                CREATE INDEX notifications_safetynotification_0f8b1c70 ON notifications_safetynotification USING btree (safety_type);

                CREATE INDEX pki_certificate_cn_3e2d4af88aa8198b_like ON pki_certificate USING btree (cn varchar_pattern_ops);

                CREATE INDEX pki_certificate_e8701ad4 ON pki_certificate USING btree (user_id);

                CREATE INDEX reversion_revision_e8701ad4 ON reversion_revision USING btree (user_id);

                CREATE INDEX reversion_version_417f1b1c ON reversion_version USING btree (content_type_id);

                CREATE INDEX reversion_version_5de09a8d ON reversion_version USING btree (revision_id);

                CREATE INDEX scratchpad_scratchpad_1dd9cfcc ON scratchpad_scratchpad USING btree (submission_id);

                CREATE INDEX scratchpad_scratchpad_5e7b1936 ON scratchpad_scratchpad USING btree (owner_id);

                CREATE INDEX submission_registered_countrie_country_id_3bce23ecf6104140_like ON submission_registered_countries USING btree (country_id varchar_pattern_ops);

                CREATE INDEX submission_registered_countries_93bfec8a ON submission_registered_countries USING btree (country_id);

                CREATE INDEX submission_registered_countries_d1fbd48c ON submission_registered_countries USING btree (submissionform_id);

                CREATE INDEX tasks_task_02c1725c ON tasks_task USING btree (assigned_to_id);

                CREATE INDEX tasks_task_417f1b1c ON tasks_task USING btree (content_type_id);

                CREATE INDEX tasks_task_7d1bc432 ON tasks_task USING btree (task_type_id);

                CREATE INDEX tasks_task_e93cb7eb ON tasks_task USING btree (created_by_id);

                CREATE INDEX tasks_task_expedited_review_categories_57746cc8 ON tasks_task_expedited_review_categories USING btree (task_id);

                CREATE INDEX tasks_task_expedited_review_categories_b15936f1 ON tasks_task_expedited_review_categories USING btree (expeditedreviewcategory_id);

                CREATE INDEX tasks_tasktype_groups_0e939a4f ON tasks_tasktype_groups USING btree (group_id);

                CREATE INDEX tasks_tasktype_groups_ff91ec0d ON tasks_tasktype_groups USING btree (tasktype_id);

                CREATE INDEX users_invitation_e8701ad4 ON users_invitation USING btree (user_id);

                CREATE INDEX users_invitation_uuid_6f2c7076a34547ea_like ON users_invitation USING btree (uuid varchar_pattern_ops);

                CREATE INDEX users_loginhistory_e8701ad4 ON users_loginhistory USING btree (user_id);

                CREATE INDEX users_userprofile_66c5cb32 ON users_userprofile USING btree (communication_proxy_id);

                CREATE INDEX votes_vote_abde9629 ON votes_vote USING btree (submission_form_id);

                CREATE INDEX workflow_edge_22d0d145 ON workflow_edge USING btree (from_node_id);

                CREATE INDEX workflow_edge_33b4eced ON workflow_edge USING btree (to_node_id);

                CREATE INDEX workflow_edge_982f3855 ON workflow_edge USING btree (guard_id);

                CREATE INDEX workflow_guard_417f1b1c ON workflow_guard USING btree (content_type_id);

                CREATE INDEX workflow_node_1ec0e39d ON workflow_node USING btree (graph_id);

                CREATE INDEX workflow_node_9f9d94c8 ON workflow_node USING btree (data_ct_id);

                CREATE INDEX workflow_node_c0a26a33 ON workflow_node USING btree (node_type_id);

                CREATE INDEX workflow_nodetype_417f1b1c ON workflow_nodetype USING btree (content_type_id);

                CREATE INDEX workflow_nodetype_7470d5e5 ON workflow_nodetype USING btree (data_type_id);

                CREATE INDEX workflow_nodetype_c4ef352f ON workflow_nodetype USING btree (category);

                CREATE INDEX workflow_token_0afd9202 ON workflow_token USING btree (source_id);

                CREATE INDEX workflow_token_846c77cf ON workflow_token USING btree (workflow_id);

                CREATE INDEX workflow_token_c693ebc8 ON workflow_token USING btree (node_id);

                CREATE INDEX workflow_token_e2ea24b3 ON workflow_token USING btree (consumed_by_id);

                CREATE INDEX workflow_token_trail_17f7dbe8 ON workflow_token_trail USING btree (to_token_id);

                CREATE INDEX workflow_token_trail_7f386cc4 ON workflow_token_trail USING btree (from_token_id);

                CREATE INDEX workflow_workflow_1ec0e39d ON workflow_workflow USING btree (graph_id);

                CREATE INDEX workflow_workflow_417f1b1c ON workflow_workflow USING btree (content_type_id);

                CREATE INDEX workflow_workflow_6be37982 ON workflow_workflow USING btree (parent_id);
            ''')


def migrate_countries(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("select to_regclass('submission_registered_countries')")
        if cursor.fetchone()[0]:
            cursor.execute('''
                alter table core_submissionform
                    add column substance_p_c_t_countries character varying(2)[],
                    add column substance_registered_in_countries character varying(2)[];

                update core_submissionform sf
                    set substance_registered_in_countries = agg.countries
                    from (
                        select submissionform_id, array_agg(country_id order by country_id) as countries
                        from submission_registered_countries
                        group by submissionform_id
                    ) agg
                    where sf.id = agg.submissionform_id;

                update core_submissionform sf
                    set substance_p_c_t_countries = agg.countries
                    from (
                        select submissionform_id, array_agg(country_id order by country_id) as countries
                        from core_submissionform_substance_p_c_t_countries
                        group by submissionform_id
                    ) agg
                    where sf.id = agg.submissionform_id;

                update core_submissionform
                    set substance_registered_in_countries = '{}'::varchar(2)[]
                    where substance_registered_in_countries is null;

                update core_submissionform
                    set substance_p_c_t_countries = '{}'::varchar(2)[]
                    where substance_p_c_t_countries is null;
            ''')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_production_compat'),
    ]

    operations = [
        migrations.RunPython(rename_indices),
        migrations.RunPython(migrate_countries),
    ]
