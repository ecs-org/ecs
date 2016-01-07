import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from ecs import bootstrap
from ecs.documents.models import DocumentType
from ecs.utils import Args, gpgutils

_ = lambda s: s     # dummy gettext for marking strings

@bootstrap.register()
def document_types():
    names = (
        Args(_("Covering Letter"), "coveringletter", _("Cover letter / covering letter to the Ethics Commission")),
        Args(_("patient information"), "patientinformation", 
            _("Patients / subjects / children / youths / parents / genetic information, information for non competent patients")),
        Args(_("insurancecertificate"), "insurancecertificate", _(" ")),
        Args(_("study protocol"), "protocol", _("study protocol")),
        Args(_("Investigator's Brochure"), "investigatorsbrochure", _(" "), is_downloadable=False),
        Args(_("Amendment"), "amendment", _("Protocol changes")),
        Args(_("Curriculum Vitae (CV)"), "cv", _("CV")),
        Args(_("Conflict of Interest"), "conflictofinterest",_("can also be a Financial Disclosure Form")),
        Args(_("Case Report Form (CRF)"), "crf", _(" ")),
        Args(_("EudraCT Form"), "eudract",
            _("Request for Authorisation, Notification of Amendment Form, Declaration of the end of the clinical trial")),
        Args(_("adverse reaction report"), "adversereaction", _("Med Watch report, CIOMS form etc.")),
        Args(_("Statement on a review"), "reviewstatement", _(" ")),
        Args(_("other"), "other", _("Patient diaries, patient card, technical information, questionnaires, etc.")),

        # internal document types; not user visible
        Args(_("Submission Form"), "submissionform", _("Submission Form"), is_hidden=True),
        Args(_("Checklist"), "checklist", _("Checklist"), is_hidden=True),
        Args(_("vote"), "votes", _("Vote"), is_hidden=True),
        Args(_("Notification"), "notification", _("Notification"), is_hidden=True),
        Args(_("Notification Answer"), "notification_answer", _("Notification Answer"), is_hidden=True),
        Args(_("Invoice"), "invoice", _("Invoice"), is_hidden=True),
        Args(_("Checklist Payment"), "checklist_payment", _("Checklist Payment"), is_hidden=True),
    )

    for args in names:
        name, identifier, helptext = args
        DocumentType.objects.update_or_create(identifier=identifier, defaults={
            'name': name,
            'helptext': helptext,
            'is_hidden': args.get('is_hidden', False),
            'is_downloadable': args.get('is_downloadable', True),
        })

@bootstrap.register()
def import_encryption_sign_keys():
    if not hasattr(settings, 'STORAGE_ENCRYPT'):
        raise ImproperlyConfigured("no STORAGE_ENCRYPT setting")
    for a in "gpghome", "encrypt_key", "signing_key":
        if a not in settings.STORAGE_ENCRYPT:
            raise ImproperlyConfigured("missing parameter {0} in settings.STORAGE_ENCRYPT".format(a))

    gpgutils.reset_keystore(settings.STORAGE_ENCRYPT ["gpghome"])
    gpgutils.import_key(settings.STORAGE_ENCRYPT ["encrypt_key"], settings.STORAGE_ENCRYPT ["gpghome"])
    gpgutils.import_key(settings.STORAGE_ENCRYPT ["signing_key"], settings.STORAGE_ENCRYPT ["gpghome"])

@bootstrap.register()
def import_decryption_verify_keys():
    if not hasattr(settings, 'STORAGE_DECRYPT'):
        raise ImproperlyConfigured("no STORAGE_DECRYPT setting")
    for a in "gpghome", "decrypt_key", "verify_key":
        if a not in settings.STORAGE_DECRYPT:
            raise ImproperlyConfigured("missing parameter {0} in settings.STORAGE_DECRYPT".format(a))

    gpgutils.reset_keystore(settings.STORAGE_DECRYPT ["gpghome"])
    gpgutils.import_key(settings.STORAGE_DECRYPT ["decrypt_key"], settings.STORAGE_DECRYPT ["gpghome"])
    gpgutils.import_key(settings.STORAGE_DECRYPT ["verify_key"], settings.STORAGE_DECRYPT ["gpghome"])

@bootstrap.register()
def create_local_storage_vault():
    if not os.path.isdir(settings.STORAGE_VAULT_DIR):
        os.makedirs(settings.STORAGE_VAULT_DIR)
